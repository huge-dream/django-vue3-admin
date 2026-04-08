import {ElNotification  as message} from 'element-plus'
import {Session} from "/@/utils/storage";
import {getWsBaseURL} from "/@/utils/baseUrl";
// @ts-ignore
import socket from '@/types/api/socket'
import {useUserInfo} from "/@/stores/userInfo";
const websocket: socket = {
    websocket: null,
    connectURL: getWsBaseURL(),
    // 开启标识
    socket_open: false,
    // 心跳timer
    hearbeat_timer: null,
    // 心跳发送频率
    hearbeat_interval: 2 * 1000,
    // 是否自动重连
    is_reonnect: true,
    // 重连次数
    reconnect_count: 3,
    // 已发起重连次数
    reconnect_current: 1,
    // 重连timer
    reconnect_timer: null,
    // 重连频率
    reconnect_interval: 5 * 1000,
    init: (receiveMessage: Function | null) => {
        if (!('WebSocket' in window)) {
            message.warning('浏览器不支持WebSocket')
            return null
        }
        const token = Session.get('token')
        if(!token){
            // message.warning('websocket认证失败')
            return null
        }
        const wsUrl = `${getWsBaseURL()}ws/${token}/`
        websocket.websocket = new WebSocket(wsUrl)
        websocket.websocket.onmessage = (e: any) => {
            if (receiveMessage) {
                receiveMessage(e)
            }
        }
        websocket.websocket.onclose = (e: any) => {
            websocket.socket_open = false
            useUserInfo().setWebSocketState(websocket.socket_open);
            // 需要重新连接
            if (websocket.is_reonnect) {
                websocket.reconnect_timer = setTimeout(() => {
                    // 超过重连次数
                    if (websocket.reconnect_current > websocket.reconnect_count) {
                        clearTimeout(websocket.reconnect_timer)
                        websocket.is_reonnect = false
                        websocket.socket_open = false
                        useUserInfo().setWebSocketState(websocket.socket_open);
                        return
                    }
                    // 记录重连次数
                    websocket.reconnect_current++
                    websocket.reconnect()
                }, websocket.reconnect_interval)
            }
        }
        // 连接成功
        websocket.websocket.onopen = function () {
            websocket.socket_open = true
            useUserInfo().setWebSocketState(websocket.socket_open);
            websocket.is_reonnect = true
            // 开启心跳
            websocket.heartbeat()
        }
        // 连接发生错误
        websocket.websocket.onerror = function () { }
    },
    heartbeat: () => {
        websocket.hearbeat_timer && clearInterval(websocket.hearbeat_timer)

        websocket.hearbeat_timer = setInterval(() => {
            let data = {
                token: Session.get('token')
            }
            websocket.send(data)
        }, websocket.hearbeat_interval)
    },
    send: (data:string, callback = null) => {
        // 开启状态直接发送
        if (websocket.websocket.readyState === websocket.websocket.OPEN) {
            websocket.websocket.send(JSON.stringify(data))
            // @ts-ignore
            callback && callback()
        } else {
            clearInterval(websocket.hearbeat_timer)
            // message({
            //     type: 'warning',
            //     message: 'socket链接已断开',
            //     duration: 1000,
            // })
            websocket.socket_open = false
            useUserInfo().setWebSocketState(websocket.socket_open);
        }
    },
    close: () => {
        websocket.is_reonnect = false
        websocket.websocket.close()
        websocket.websocket = null;
        websocket.socket_open = false
        useUserInfo().setWebSocketState(websocket.socket_open);
    },
    /**
     * 重新连接
     */
    reconnect: () => {
        if (websocket.websocket && !websocket.is_reonnect) {
            websocket.close()
        }
        websocket.init(null)
    },
}
export default websocket;
