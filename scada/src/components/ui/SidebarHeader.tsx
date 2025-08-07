import React from "react";
import { useSidebar } from "../../hooks/useSidebar";

export const SidebarHeader:React.FC=()=>{
    const {state,toggleSidebar}=useSidebar();
    const isCollapsed = state === "collapsed";
    return(
        <div className="sidebar-header">
            { !isCollapsed && (
            <div className="header-content">
                <h2>Monitoring Dashboard</h2>
                <div className="status-indicator">
                    <span className="status-dot_active"></span>
                    <span>Live</span>
                </div>
            </div>
            )}
            <button
            onClick={toggleSidebar}
            className="toggle-btn"
            aria-label={isCollapsed?"Expand sidebar":"Collapse sidebar"}
            >
            {isCollapsed ? (
                <span>▶</span>
                ) : (
                <span>◀</span>
                )}
            </button>
        </div>
    );
}