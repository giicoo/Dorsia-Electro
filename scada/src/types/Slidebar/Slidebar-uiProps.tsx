
export type SidebarState = "expanded" | "collapsed";
export type SidebarContextProps = {
    state: SidebarState;
    open:boolean;
    setOpen: (open:boolean)=> void;
    toggleSidebar:()=> void;
}