import axios from '../axios'
import {base_url,debug} from '../axios'

const url = base_url+'/app'

export const net_release = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.post(url+'/release',param);
    return res
}

export const net_stop = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.post(url+'/stop',param);
    return res
}

export const net_get_state = (param) => {
    if (debug){
        return {'status':1,'state':1}
    }
    let res = axios({'method':'get','url':url+'/getState', 'params':param});
    return res
}

export const net_get_robot_list = (param) => {
    if (debug){
        return {'status':1,'app_list':[{'app_name':'nba','app_id':'nba'}]}
    }
    let res = axios({'method':'get','url':url+'/list', 'params':param});
    return res
}

export const net_add_robot = (param) => {
    if (debug){
        return {'status':1,'app_id':param['app_name']+'_id'}
    }
    let res = axios.post(url+'/add',param);
    return res;
}

export const net_delete_robot = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.get(url+'/delete',{'params':param});
    return res;
}

export const net_edit_name = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.post(url+'/editName',param);
    return res;
}

export const net_get_table_name = (param) => {
    if (debug){
        return {'status':1,'name':'nba.csv'}
    }
    let res = axios.get(url+'/getTableName',{'params':param});
    return res;
}

export const net_get_table = (param) => {
    if (debug){
        return {'status':1,'table':static_data}
    }
    let res = axios.get(url+'/getTable',{'params':param});
    return res;
}

export const net_upload_table = (param) => {
    if (debug){
        return {'status':1}
    }
    let header = { "Content-Type": "multipart/form-data" };
    let res = axios.post(url+'/uploadTable',param,{'headers':header});
    return res;
}

export const net_table_header = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.post(url+'/tableHeader',param);
    return res;
}

export const net_get_table_header = (param) => {
    if (debug){
        return {'status':1,'header':[{'col':'player_name','alias':['名字']},{'col':'team','alias':[]},{'col':'height','alias':['身高']}]}
    }
    let res = axios.get(url+'/getTableHeader',{'params':param});
    return res;
}

export const net_get_table_col = (param) => {
    if (debug){
        return {'status':1,'header':[{'col':'player_name','alias':['名字']},{'col':'team','alias':[]},{'col':'height','alias':['身高']}]}
    }
    let res = axios.get(url+'/getTableCol',{'params':param});
    return res;
}

export const net_table_type = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.post(url+'/tableType',param);
    return res;
}

export const net_get_table_type = (param) => {
    if (debug){
        return {'status':1,'type':[]};
    }
    let res = axios.get(url+'/getTableType',{'params':param});
    return res;
}

export const net_get_join_keys = (param) => {
    if (debug){
        return {'status':1,'keys':[]}
    }
    let res = axios.get(url+'/getJoinKeys',{'params':param});
    return res;
}

export const net_join_keys = (param) => {
    if (debug){
        return {'status':1,'keys':[]}
    }
    let res = axios.post(url+'/joinKeys',param);
    return res;
}

export const net_nlg = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.post(url+'/nlg',param);
    return res;
}

export const net_get_nlg = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.get(url+'/getNlg',{'params':param});
    return res;
}

export const net_slu = (param) => {
    if (debug){
        return {'status':1,'rules':[]}
    }
    let res = axios.post(url+'/slu',param);
    return res;
}

export const net_get_slu = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.get(url+'/getSlu',{'params':param});
    return res;
}

export const net_entity = (param) => {
    if (debug){
        return {'status':1}
    }
    let res = axios.post(url+'/entity',param);
    return res;
}

export const net_get_entity = (param) => {
    if (debug){
        return {'status':1,'entity':'player_name','entity_alias':'','entity_adj':[]}
    }
    let res = axios.get(url+'/getEntity',{'params':param});
    return res;
}

var static_data = [{
    player_id:'1962937408',
    player_name:'本-西蒙斯',
    player_no:'25',
    player_position:'后卫-前锋',
    player_height_cm:'208',
    player_weight_kg:'104.3',
    player_birth_day:'1996-07-20',
    player_team:'76人',
    player_draft_year:'2016',
    player_time_min:'34.2',
    player_point:'16.9',
    player_goal_percent_all:'56.3',
    player_shot_success_all:'6.8',
    player_shot_number_all:'12.2',
    player_goal_percent_3p:'0',
    player_shot_success_3p:'0',
    player_shot_number_3p:'0.1',
    player_goal_percent_penalty_shot:'60',
    player_shot_success_penalty_shot:'3.3',
    player_shot_number_penalty_shot:'5.4',
    player_rebound:'8.8',
    player_rebound_front:'2.2',
    player_rebound_back:'6.6',
    player_assists:'7.7',
    player_stealing:'1.4',
    player_blocking:'0.8',
    player_foul:'2.6',
}];