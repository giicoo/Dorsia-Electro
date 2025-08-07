import { ReactNode } from "react";
import { JSX } from "react/jsx-runtime";

export interface MonitoringSlidebarProps{
    children: ReactNode;
    currentView:string;
    setCurrentView:(view:string)=> void;
}

export interface MonitoringItemProps{
    icon: React.ReactNode;
    title: string;
    value: valueTypeProps;
    trend?:'up'|'down';
    onClick?:()=> void;
}
type valueTypeProps = {  // Изменили тип value
    title: string;
    icon:React.JSX.Element
  }[];

export type MonitoringTypeProps={
    map(arg0: (item: any, index: any) => JSX.Element): ReactNode;
    title: string;
    
    items: {
        title: string;
      }[];
}