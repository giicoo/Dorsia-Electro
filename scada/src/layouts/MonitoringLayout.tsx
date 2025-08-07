import { title } from "process";
import { MonitoringItem } from "../components/Slidebar/MonitoringItem";
import { MonitoringTypeProps } from "../types/Slidebar/SlidevarProps";
import { ActivityIcon, AlertTriangleIcon, BarChart3, ChartLine, Clock, Database, FileText, Gauge, Monitor, SettingsIcon, Shield, TrendingUp } from "lucide-react";

const navigationItems = [
    {
        title:'Главная панель',
        items:[
            {title:'Обзор системы',icon:<BarChart3 />},
            {title:'Мониторинг в реальном времени',icon:<ActivityIcon />},
        ],
        
    },
    {
        title:"Диагностика",
        items:[
            {title:'Токовая диагностика',icon:<Gauge />},
            {title:'Классификация дефектов',icon:<Shield />},
            {title:'Отчеты диагностики',icon:<FileText />},

        ]
    },
    {
        title:'SCADA системы',
        items:[
            {title:"Промышленная SCADA",icon:<Monitor />},
            {title:"Управление процессами",icon:<SettingsIcon />}
        ]
    },
    {
        title:"Grafana аналитика",
        items:[
            {title:"Временные ряды",icon:<ChartLine />},
            {title:"Мониторинг ",icon:<TrendingUp />}
        ]
    },
    {
        title:"CMMS",
        items:[
            {title:"Планирование ТО",icon:<Clock />},
            {title:"Упралвение активами",icon: <Database />},
            {title:"Уведомления",icon: <AlertTriangleIcon />}
        ]
    }
]

export const MonitoringSlidebar = () => {
    return (
        <div className="sidebar">
            {navigationItems.map((section,index)=> (
                <MonitoringItem key={index} title={section.title} icon={undefined} value={section.items}></MonitoringItem>))}
        </div>
    )
}

export default navigationItems;