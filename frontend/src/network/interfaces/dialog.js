import axios from '../axios'
import { base_url, debug } from '../axios'

const url = base_url + '/dialog'

export const net_get_response = (param) => {
	if (debug) {
		return { 'status': 1, 'response': param['message'] }
	}
	let res = axios.post(url + '/chat', param);
	return res
}

export const net_find_robot = (param) => {
	if (debug) {
		if (param['domain'] != "NBA")
			return { 'status': 1, 'exist': false }
		else
			return { 'status': 1, 'exist': true }
	}
	let res = axios.get(url + '/find', { 'params': param })
	return res
}

export const net_save_actions = (param) => {
	let res = axios.post("/saveActions", param)
	return res
}

export const net_get_actions = (param) => {
	let res = axios.get("/getActions", param)
	return res
}

export const net_do_action = (param) => {
	let res = axios.post("/doAction", param)
	return res
}

export const net_get_screenshot = (param) => {
	let res = axios.get("/getScreenshot?uid=" + param["uid"])
	return res
}

export const net_get_dialog = (params) => {
	let res = axios.get("/getDialog?dialog_id="+params["dialog_id"])
	return res
}

export const net_start_record = (param) => {
	let res = axios.post("/startRecord", param);
	return res;
}

export const net_end_record = (param) => {
	let res = axios.post("/endRecord", param);
	return res;
}

export const net_reset = (param) => {
	let res = axios.post("/reset", param);
	return res;
}

export const net_save = (param) => {
	let res = axios.post("/save", param);
	return res;
}

export const net_save_review = (param) => {
	let res = axios.post("/saveReview", param);
	return res;
}

export const net_get_review = (param) => {
	let res = axios.get(`/getReview?uid=${param["uid"]}&dialog=${param["dialog"]}&turn=${param["turn"]}`);
	return res;
}

export const net_get_review_dialog = (param) => {
	let res = axios.get("/getReviewDialog?uid="+param["uid"])
	return res
}

export const net_get_all_dialog = (param) => {
	let res = axios.get("/getAllDialog?uid="+param["uid"])
	return res
}

export const net_get_goal = () => {
	let res = axios.get("/goalsGenerator")
	return res
}

export const net_add_turn = (param) => {
	let res = axios.get(`/addDialog?dialog=${param["dialog"]}&turn=${param["turn"]}`);
	return res;
}

export const net_delete_turn = (param) => {
	let res = axios.get(`/deleteDialog?dialog=${param["dialog"]}&turn=${param["turn"]}`);
	return res;
}

export const net_get_new_dialog = (param) => {
	let res = axios.get("/getNewDialog?uid="+param["uid"])
	return res
}