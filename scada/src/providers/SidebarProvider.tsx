import React, {  ReactNode, useState } from "react";
import { MonitoringSlidebarProps } from "../types/Slidebar/SlidevarProps";
import { SidebarContextProps, SidebarState } from "../types/Slidebar/Slidebar-uiProps";

export const sidebarContext = React.createContext<SidebarContextProps | undefined>(undefined);
export const SidebarProvider:React.FC< {children: ReactNode}>=({children})=>{
    const [open,setOpen] = useState(true);

    const state: SidebarState = open ? "expanded" : "collapsed";
    const toggleSidebar = () => {
        setOpen(prev => !prev);
    };

    return(
        <sidebarContext.Provider value={{
            state,
            open,
            setOpen,
            toggleSidebar
        }}>
            {children}
        </sidebarContext.Provider>
    )

}