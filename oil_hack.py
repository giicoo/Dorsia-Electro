import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch, find_peaks
import os
import warnings
from tqdm import tqdm
import numba as nb
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI

# Отключение предупреждений
warnings.filterwarnings('ignore')

# === 1. Настройки ===
PATH = 'C:/Work/Hack/Neft/Data_Set_main/current_'
EXCLUDE_FILES = {11, 15, 17, 19, 21, 23, 25, 27, 31}
FS = 25600
RPM = 1770
F_SUPPLY = 60
S = 0.0167
MAX_PLOT_POINTS = 500000
PARK_SAMPLE_SIZE = 50000
N_POLES = 4  # Количество полюсов

# Параметры подшипника NSK6205DDU
N_BALLS = 9
D_BALL = 7.94e-3
D_CAGE = 39e-3
CONTACT_ANGLE = 0  # Угол контакта

# Пороги для обнаружения дефектов
BEARING_THRESHOLD = 0.01
ROTOR_THRESHOLD = 0.01
STATOR_THRESHOLD = 0.01
ECCENTRICITY_THRESHOLD = 0.01

# === 2. Оптимизированная загрузка данных ===
def load_data():
    """Загружает данные с использованием итераторов и оптимизированных типов"""
    data = {'current_R': [], 'current_S': [], 'current_T': []}
    file_indices = [i for i in range(1, 39) if i not in EXCLUDE_FILES]
    
    for i in tqdm(file_indices, desc="Загрузка файлов"):
        file_path = f'{PATH}{i}.csv'
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            continue
            
        try:
            # Чтение только нужных столбцов с оптимизированным типом
            df = pd.read_csv(file_path, usecols=['current_R', 'current_S', 'current_T'], dtype=np.float32)
            for ch in data.keys():
                if ch in df.columns:
                    data[ch].append(df[ch].values)
        except Exception as e:
            print(f"Ошибка при обработке файла {i}: {str(e)}")
    
    return {k: np.concatenate(v).astype(np.float32) for k, v in data.items()}

# === 3. Функции для диагностики ===
def calculate_rms(current):
    return np.sqrt(np.mean(current**2))

def compute_welch(current, fs, nperseg=8192):
    freqs, psd = welch(
        current,
        fs=fs,
        nperseg=nperseg,
        average='median',
        scaling='spectrum'
    )
    return freqs, np.sqrt(psd)

def calculate_bearing_frequencies(f_rotor):
    """Расчет частот дефектов подшипника"""
    bearing_ratio = D_BALL / D_CAGE
    cos_beta = np.cos(CONTACT_ANGLE)
    
    # Частота вращения сепаратора
    f_cage = f_rotor * 0.5 * (1 - bearing_ratio * cos_beta)
    
    # Внешняя дорожка качения
    BPFO = f_rotor * 0.5 * N_BALLS * (1 - bearing_ratio * cos_beta)
    
    # Внутренняя дорожка качения
    BPFI = f_rotor * 0.5 * N_BALLS * (1 + bearing_ratio * cos_beta)
    
    # Частота вращения тел качения
    BSF = f_rotor * 0.5 * (D_CAGE / D_BALL) * (1 - (bearing_ratio ** 2) * (cos_beta ** 2))
    
    return BPFO, BPFI, BSF, f_cage

def calculate_rotor_defect_frequencies(f_supply, slip):
    """Расчет частот для дефектов ротора"""
    sidebands = [f_supply - 2*slip*f_supply, f_supply + 2*slip*f_supply]
    
    harmonic_sidebands = []
    for k in range(1, 4):
        harmonic_sidebands.extend([
            (1 - 2*k*slip)*f_supply,
            (1 + 2*k*slip)*f_supply
        ])
    
    return sidebands, harmonic_sidebands

def calculate_eccentricity_frequencies(f_supply, f_rotor, n_poles):
    """Расчет частот для эксцентриситета"""
    static_eccentricity = [f_supply]
    dynamic_eccentricity = [f_supply + k*f_rotor for k in range(1, 4)]
    mixed_eccentricity = [k * (f_supply / n_poles) for k in range(1, 5)]
    
    return static_eccentricity, dynamic_eccentricity, mixed_eccentricity

def calculate_stator_defect_frequencies(f_supply):
    """Расчет частот для дефектов статора"""
    turn_fault = [2*f_supply, 3*f_supply]
    phase_asymmetry = [f_supply]
    short_circuit = [f_supply, 3*f_supply]
    
    return turn_fault, phase_asymmetry, short_circuit

@nb.njit(fastmath=True, parallel=True)
def optimized_park_transform(I_R, I_S, I_T, theta):
    n = len(I_R)
    I_d = np.empty(n, dtype=np.float32)
    I_q = np.empty(n, dtype=np.float32)
    
    for i in nb.prange(n):
        I_alpha = I_R[i] - 0.5*I_S[i] - 0.5*I_T[i]
        I_beta = (np.sqrt(3)/2)*(I_S[i] - I_T[i])
        cos_theta = np.cos(theta[i])
        sin_theta = np.sin(theta[i])
        I_d[i] = I_alpha * cos_theta + I_beta * sin_theta
        I_q[i] = -I_alpha * sin_theta + I_beta * cos_theta
        
    return I_d, I_q

def detect_defects(freqs, magnitudes, defect_freqs, threshold=0.01, tolerance=2.0):
    """Обнаружение дефектов по характерным частотам"""
    peaks, properties = find_peaks(
        magnitudes, 
        height=threshold*np.max(magnitudes),
        prominence=0.1*np.max(magnitudes)
    )
    
    detected_defects = []
    peak_freqs = freqs[peaks]
    peak_mags = properties['peak_heights']
    
    main_harmonic_idx = np.argmin(np.abs(freqs - F_SUPPLY))
    main_harmonic_mag = magnitudes[main_harmonic_idx]
    
    for defect_freq in defect_freqs:
        for peak_freq, peak_mag in zip(peak_freqs, peak_mags):
            if abs(peak_freq - defect_freq) < tolerance:
                severity = min(1.0, peak_mag / max(1e-6, main_harmonic_mag))
                detected_defects.append((defect_freq, peak_mag, severity))
                break
    
    return detected_defects

def analyze_bearing_condition(defect_list):
    if not defect_list:
        return "Норма", 0.0
    
    total_severity = sum(severity for _, _, severity in defect_list) / len(defect_list)
    
    if total_severity < 0.1:
        return "Норма", total_severity
    elif total_severity < 0.3:
        return "Начальная стадия", total_severity
    elif total_severity < 0.6:
        return "Развитая стадия", total_severity
    else:
        return "Критическое состояние", total_severity

def analyze_rotor_condition(defect_list):
    if not defect_list:
        return "Норма", 0.0
    
    total_severity = sum(severity for _, _, severity in defect_list) / len(defect_list)
    
    if total_severity < 0.05:
        return "Норма", total_severity
    elif total_severity < 0.2:
        return "Начальная стадия", total_severity
    elif total_severity < 0.4:
        return "Развитая стадия", total_severity
    else:
        return "Критическое состояние", total_severity

def analyze_stator_condition(defect_list, phase_asymmetry):
    asym_severity = abs(phase_asymmetry - 1) * 100
    other_severity = sum(severity for _, _, severity in defect_list) / max(1, len(defect_list))
    total_severity = max(asym_severity / 100, other_severity)
    
    if asym_severity < 5 and not defect_list:
        return "Норма", total_severity
    elif asym_severity < 10 and total_severity < 0.2:
        return "Начальная стадия", total_severity
    elif asym_severity < 20 or total_severity < 0.4:
        return "Развитая стадия", total_severity
    else:
        return "Критическое состояние", total_severity

def analyze_eccentricity_condition(defect_list):
    if not defect_list:
        return "Норма", 0.0
    
    total_severity = sum(severity for _, _, severity in defect_list) / len(defect_list)
    
    if total_severity < 0.1:
        return "Норма", total_severity
    elif total_severity < 0.3:
        return "Начальная стадия", total_severity
    elif total_severity < 0.6:
        return "Развитая стадия", total_severity
    else:
        return "Критическое состояние", total_severity

def create_pdf_report(report_data, images):
    """Создает PDF отчет с результатами диагностики"""
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
    font_pathB = os.path.join(os.path.dirname(__file__), 'DejaVuSans-Bold.ttf')
    # Добавить шрифт с поддержкой Unicode
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.add_font('DejaVu', 'B', font_pathB, uni=True)
    pdf.set_font("DejaVu", size=12)
    
    # Заголовок
    pdf.set_font("DejaVu", 'B', 16)
    pdf.cell(200, 10, txt="Отчет по диагностике асинхронного двигателя", ln=1, align='C')
    pdf.ln(10)
    
    # Информация о двигателе
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(200, 10, txt="Характеристики двигателя:", ln=1)
    pdf.set_font("DejaVu", size=12)
    pdf.cell(200, 8, txt=f"Тип: Асинхронный, {report_data['power']} кВт", ln=1)
    pdf.cell(200, 8, txt=f"Номинальная скорость: {report_data['rpm']} об/мин", ln=1)
    pdf.cell(200, 8, txt=f"Частота сети: {report_data['f_supply']} Гц", ln=1)
    pdf.cell(200, 8, txt=f"Подшипник: {report_data['bearing']}", ln=1)
    pdf.ln(5)
    
    # Результаты диагностики
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(200, 10, txt="Результаты диагностики:", ln=1)
    pdf.set_font("DejaVu", size=12)
    
    components = [
        ("Подшипники", report_data['bearing_condition'], report_data['bearing_severity']),
        ("Ротор", report_data['rotor_condition'], report_data['rotor_severity']),
        ("Статор", report_data['stator_condition'], report_data['stator_severity']),
        ("Эксцентриситет", report_data['eccentricity_condition'], report_data['eccentricity_severity'])
    ]
    
    for component, condition, severity in components:
        status = f"{component}: {condition} (серьезность: {severity:.2f})"
        pdf.cell(200, 8, txt=status, ln=1)
    
    pdf.cell(200, 8, txt=f"Асимметрия фаз: {report_data['phase_asymmetry']*100:.1f}%", ln=1)
    pdf.ln(5)
    
    # Рекомендации
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(200, 10, txt="Рекомендации:", ln=1)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 8, report_data['recommendations'])
    pdf.ln(10)
    
    # Графики
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(200, 10, txt="Графики анализа:", ln=1)
    
    for img_path in images:
        pdf.image(img_path, x=10, w=190)
        pdf.ln(5)
    
    # Сохранение отчета
    output_path = os.path.join(os.path.dirname(__file__), 'motor_diagnosis_report.pdf')
    #pdf.output("motor_diagnosis_report.pdf")
    pdf.output(output_path)
    return "motor_diagnosis_report.pdf"

# === 4. Основная программа ===
if __name__ == "__main__":
    print("=== Диагностика асинхронного двигателя 3 кВт ===")
    print(f"Тип подшипника: NSK6205DDU, Количество тел качения: {N_BALLS}")
    
    # 1. Загрузка данных
    print("\nЗагрузка данных...")
    data = load_data()
    I_R, I_S, I_T = data['current_R'], data['current_S'], data['current_T']
    total_points = len(I_R)
    print(f"Загружено {total_points/1e6:.2f} млн точек данных")
    
    # 2. Временные параметры
    t = np.arange(total_points) / FS
    f_rotor = RPM / 60
    
    # 3. Проверка симметрии фаз
    rms_R = calculate_rms(I_R)
    rms_S = calculate_rms(I_S)
    rms_T = calculate_rms(I_T)
    avg_rms = (rms_R + rms_S + rms_T) / 3
    phase_asymmetry = max(abs(rms_R - avg_rms), abs(rms_S - avg_rms), abs(rms_T - avg_rms)) / avg_rms
    
    print(f"\nRMS токов: R={rms_R:.2f} А, S={rms_S:.2f} А, T={rms_T:.2f} А")
    print(f"Асимметрия фаз: {phase_asymmetry*100:.1f}%")
    
    # 4. Спектральный анализ
    print("\nСпектральный анализ...")
    freqs, mag_R = compute_welch(I_R, FS)
    
    # 5. Расчет характерных частот
    print("\nРасчет характерных частот дефектов:")
    
    # 5.1. Подшипник
    BPFO, BPFI, BSF, f_cage = calculate_bearing_frequencies(f_rotor)
    bearing_freqs = [BPFO, BPFI, BSF, f_cage, BPFO*2, BPFI*2, BPFO+BPFI]
    print(f"Подшипник: BPFO={BPFO:.1f} Гц, BPFI={BPFI:.1f} Гц, BSF={BSF:.1f} Гц, Сепаратор={f_cage:.1f} Гц")
    
    # 5.2. Ротор
    rotor_sidebands, rotor_harmonics = calculate_rotor_defect_frequencies(F_SUPPLY, S)
    rotor_freqs = rotor_sidebands + rotor_harmonics
    print(f"Ротор: боковые полосы={rotor_sidebands}, гармоники={rotor_harmonics}")
    
    # 5.3. Эксцентриситет
    static_ecc, dynamic_ecc, mixed_ecc = calculate_eccentricity_frequencies(F_SUPPLY, f_rotor, N_POLES)
    eccentricity_freqs = static_ecc + dynamic_ecc + mixed_ecc
    print(f"Эксцентриситет: статический={static_ecc}, динамический={dynamic_ecc}, смешанный={mixed_ecc}")
    
    # 5.4. Статор
    turn_fault, phase_asym_freq, short_circuit = calculate_stator_defect_frequencies(F_SUPPLY)
    stator_freqs = turn_fault + phase_asym_freq + short_circuit
    print(f"Статор: межвитковые={turn_fault}, асимметрия={phase_asym_freq}, КЗ={short_circuit}")
    
    # 6. Обнаружение дефектов
    print("\nОбнаружение дефектов:")
    
    # 6.1. Подшипник
    bearing_defects = detect_defects(freqs, mag_R, bearing_freqs, BEARING_THRESHOLD)
    bearing_condition, bearing_severity = analyze_bearing_condition(bearing_defects)
    print(f"Состояние подшипника: {bearing_condition} (серьезность: {bearing_severity:.2f})")
    
    # 6.2. Ротор
    rotor_defects = detect_defects(freqs, mag_R, rotor_freqs, ROTOR_THRESHOLD)
    rotor_condition, rotor_severity = analyze_rotor_condition(rotor_defects)
    print(f"Состояние ротора: {rotor_condition} (серьезность: {rotor_severity:.2f})")
    
    # 6.3. Статор
    stator_defects = detect_defects(freqs, mag_R, stator_freqs, STATOR_THRESHOLD)
    stator_condition, stator_severity = analyze_stator_condition(stator_defects, phase_asymmetry)
    print(f"Состояние статора: {stator_condition} (серьезность: {stator_severity:.2f})")
    
    # 6.4. Эксцентриситет
    eccentricity_defects = detect_defects(freqs, mag_R, eccentricity_freqs, ECCENTRICITY_THRESHOLD)
    eccentricity_condition, eccentricity_severity = analyze_eccentricity_condition(eccentricity_defects)
    print(f"Эксцентриситет воздушного зазора: {eccentricity_condition} (серьезность: {eccentricity_severity:.2f})")
    
    # 7. Преобразование Парка с улучшенной подвыборкой
    print("\nАнализ преобразования Парка...")
    
    # Оптимизированная подвыборка: равномерное распределение по всему набору данных
    sample_indices = np.linspace(0, total_points-1, PARK_SAMPLE_SIZE, dtype=int)
    
    I_R_sample = I_R[sample_indices]
    I_S_sample = I_S[sample_indices]
    I_T_sample = I_T[sample_indices]
    t_sample = t[sample_indices]
    
    theta_sample = 2 * np.pi * f_rotor * t_sample
    I_d, I_q = optimized_park_transform(I_R_sample, I_S_sample, I_T_sample, theta_sample)
    
    # Анализ компонент dq
    dq_ratio = np.std(I_d) / np.std(I_q)
    print(f"Отношение SD(I_d)/SD(I_q) = {dq_ratio:.3f}")
    
    # 8. Визуализация результатов
    print("\nВизуализация результатов...")
    
    # 8.1. Спектр с характерными частотами
    plt.figure(figsize=(14, 8))
    plt.semilogy(freqs, mag_R, label='Спектр фазы R')
    plt.axvline(F_SUPPLY, color='r', linestyle='--', label='Основная гармоника')
    
    # Подшипник
    for freq in bearing_freqs:
        plt.axvline(freq, color='g', linestyle=':', alpha=0.7, label='Подшипник' if freq == bearing_freqs[0] else "")
    
    # Ротор
    for freq in rotor_freqs:
        plt.axvline(freq, color='b', linestyle='-.', alpha=0.7, label='Ротор' if freq == rotor_freqs[0] else "")
    
    # Статор
    for freq in stator_freqs:
        plt.axvline(freq, color='m', linestyle='--', alpha=0.7, label='Статор' if freq == stator_freqs[0] else "")
    
    plt.xlim(0, 500)
    plt.xlabel('Частота, Гц')
    plt.ylabel('Амплитуда')
    plt.title('Спектр тока с характерными частотами дефектов')
    plt.legend()
    plt.grid()
    spectrum_img = 'defect_spectrum.png'
    plt.savefig(spectrum_img, dpi=300)
    plt.close()
    
    # 8.2. Диаграмма dq
    plt.figure(figsize=(8, 8))
    plt.scatter(I_d, I_q, s=1, alpha=0.3)
    plt.xlabel('I_d')
    plt.ylabel('I_q')
    plt.title('Диаграмма Парка')
    plt.grid()
    plt.axis('equal')
    park_img = 'park_diagram.png'
    plt.savefig(park_img, dpi=300)
    plt.close()
    
    # 8.3. График асимметрии фаз
    plt.figure(figsize=(10, 6))
    phases = ['Фаза R', 'Фаза S', 'Фаза T']
    rms_values = [rms_R, rms_S, rms_T]
    plt.bar(phases, rms_values, color=['red', 'green', 'blue'])
    plt.title('Сравнение RMS токов по фазам')
    plt.ylabel('RMS ток, А')
    plt.grid(axis='y')
    asymmetry_img = 'phase_asymmetry.png'
    plt.savefig(asymmetry_img, dpi=300)
    plt.close()
    
    # 9. Формирование рекомендаций
    recommendations = ""
    critical = bearing_severity > 0.3 or rotor_severity > 0.3 or stator_severity > 0.3 or eccentricity_severity > 0.3
    moderate = bearing_severity > 0.1 or rotor_severity > 0.1 or stator_severity > 0.1 or eccentricity_severity > 0.1
    
    if critical:
        recommendations = "ТРЕБУЕТСЯ СРОЧНОЕ ТЕХНИЧЕСКОЕ ОБСЛУЖИВАНИЕ! Обнаружены критические дефекты, которые могут привести к выходу двигателя из строя. Необходимо немедленно остановить оборудование и провести ремонт."
    elif moderate:
        recommendations = "Рекомендуется плановое обслуживание в ближайшее время. Обнаружены развивающиеся дефекты, которые могут привести к ухудшению работы двигателя. Проведите диагностику вибрации для уточнения состояния."
    else:
        recommendations = "Двигатель в хорошем состоянии. Продолжайте плановое обслуживание согласно графику. Рекомендуется периодический мониторинг состояния."
    
    # 10. Формирование данных для отчета
    report_data = {
        'power': 3,
        'rpm': RPM,
        'f_supply': F_SUPPLY,
        'bearing': f"NSK6205DDU (N={N_BALLS})",
        'bearing_condition': bearing_condition,
        'bearing_severity': bearing_severity,
        'rotor_condition': rotor_condition,
        'rotor_severity': rotor_severity,
        'stator_condition': stator_condition,
        'stator_severity': stator_severity,
        'eccentricity_condition': eccentricity_condition,
        'eccentricity_severity': eccentricity_severity,
        'phase_asymmetry': phase_asymmetry,
        'recommendations': recommendations
    }
    
    # 11. Создание PDF отчета
    pdf_path = create_pdf_report(report_data, [spectrum_img, park_img, asymmetry_img])
    
    print("\n=== Итоговый отчет по диагностике ===")
    print(f"1. Подшипники: {bearing_condition} (серьезность: {bearing_severity:.2f})")
    print(f"2. Ротор: {rotor_condition} (серьезность: {rotor_severity:.2f})")
    print(f"3. Статор: {stator_condition} (серьезность: {stator_severity:.2f})")
    print(f"4. Эксцентриситет: {eccentricity_condition} (серьезность: {eccentricity_severity:.2f})")
    print(f"5. Асимметрия фаз: {phase_asymmetry*100:.1f}%")
    print(f"\nРекомендации: {recommendations}")
    print(f"\nДиагностика завершена. Отчет сохранен в файле: {pdf_path}")