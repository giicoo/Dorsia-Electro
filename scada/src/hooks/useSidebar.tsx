import React from "react";
import { sidebarContext } from "../providers/SidebarProvider";


export const useSidebar = () =>{
    const context = React.useContext(sidebarContext);
    if(!context){
        throw new Error("useSidebar must be used within a SidebarProvider.");

    }
    return context;
}