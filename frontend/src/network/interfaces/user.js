import axios from '../axios'
import {base_url,debug} from '../axios'

const url = base_url+'/user'

export const net_login = (param) => {
    if (debug){
        return {'status':1,'user_id':param['usn'],'token':'temptoken'}
    }
    let res = axios.post(url+'/login', param);
    return res
}

export const net_register = (param) => {
    if (debug){
        return {'status':1,'user_id':param['usn']}
    }
    let res = axios.post(url+'/register', param);
    return res
}