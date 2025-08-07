import React, { ReactNode } from "react";
import { MonitoringItemProps, MonitoringTypeProps } from "../../types/Slidebar/SlidevarProps";
import { useSidebar } from "../../hooks/useSidebar";
import Images from "../../utils/Images";

export const MonitoringItem: React.FC<MonitoringItemProps>=({
    icon,
    title,
    value,
    trend,
    
    onClick
})=>{
    const {state} = useSidebar();
    const isCollapsed = state === 'collapsed';
    return(
        <div className={`monitoring-item ${
            isCollapsed? 'collapsed': 'expanded'
            }`}
            onClick={onClick}
            >
            <div className="item-icon">{icon}</div>
            {!isCollapsed && (
                <div className="item-content">
                    <div className="item-title">{title}</div>
                    <div className="item-value">
                        {/*Надо проверить возможны ошибки*/}
                        {value.map((item,index)=>(
                            <div className="sub-item" key={index}>
                                <div className="icon-item" key={index}>{item.icon}</div>
                                
                                <p className={"item-p-"+index.toString()}>{item.title}</p>
                            </div>
                        ))}
                        {trend&&(
                            <span className={`trend-indicator ${trend}`}>
                                {trend === "up" ? '↑' : '↓'};
                            </span>
                        )}
                    </div>
                </div>
            )}

        </div>
    )
}