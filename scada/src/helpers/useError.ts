import { SetStateAction, useCallback, useEffect, useState } from "react"

const useError = (err = null)=>{
    const [error,setError] = useState(err);

    useEffect(()=>{
        if(error)
            throw error;

    },[error]);

    const dispatchError = useCallback(()=>{
        setError(err);
    },[]);

    return dispatchError;
}