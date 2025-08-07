import React from "react";
import { MonitoringSlidebarProps } from "../../types/Slidebar/SlidevarProps";
import { useSidebar } from "../../hooks/useSidebar";
import { SidebarHeader } from "../ui/SidebarHeader";

export const MonitoringSlidebar: React.FC<MonitoringSlidebarProps> = ({
children,
currentView,
setCurrentView
})=>{
    const {state} = useSidebar();
    const isCollapsed = state === "collapsed";

    return(
        <aside
            className={`monitoring-slidebar ${state}`}
            data-current-view={currentView}
        >
            <SidebarHeader />

            <div className="slidebar-content">
                <div className="view-switcher">
                    <button
                    className={`view-btn ${currentView === 'overview' ? 'active':''}`}
                    onClick={()=> setCurrentView('overview')}
                    >
                        {!isCollapsed && 'Overview'}
                    </button>
                    <button
                    className={`view-btn ${currentView === 'analytics' ? 'active':''}`}
                    onClick={()=> setCurrentView('analytics')}
                    >
                        {!isCollapsed && 'Analytics'}
                    </button>
                    <button
                    className={`view-btn ${currentView === 'alerts' ? 'active':''}`}
                    onClick={()=> setCurrentView('alerts')}
                    >
                        {!isCollapsed && 'Alerts'}
                    </button>
                </div>
                <div className="monitoring-widgets">
                    {children}
                </div>
            </div>

        </aside>
    )
}