import { useMemo, useState } from "react"


const useMap=<T extends Map<any,any>>(initialValue:T)=>{
   
    const [map,setMap] = useState(new Map(initialValue));

    const actions = useMemo(
        ()=>({
            set: (key:any,value:any)=>
                setMap((prevMap)=>{
                    const nextMap = new Map(prevMap);
                    nextMap.set(key,value);
                    return nextMap;
                }),
            remove: (key:any)=>
                setMap((prevMap)=>{
                    const nextMap = new Map(prevMap);
                    nextMap.delete(key);
                    return nextMap;
                }),
            clear:()=> setMap(new Map())
        }),
        [setMap]
    );

    return [map,actions];
}
