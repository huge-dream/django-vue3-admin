import mitt, { Emitter } from 'mitt';

export interface TaskProps {
	name: string;
	custom?: any;
}

// 定义自定义事件类型
export type BusEvents = {
	onNewTask: TaskProps | undefined;
};

export interface Task {
	id: number;
	handle: string;
	data: any;
	createTime: Date;
	custom?: any;
}

export interface Core {
	bus: Emitter<BusEvents>;
	// eslint-disable-next-line no-unused-vars
	showNotification(body: string, title?: string): Notification | undefined;
	taskList: Map<String, Task>;
}

const bus = mitt<BusEvents>();
export function getSystemNotification(body: string, title?: string) {
	if (!title) {
		title = '通知';
	}
	return new Notification(title ?? '通知', {
		body: body,
	});
}
export function showSystemNotification(body: string, title?: string): Notification | undefined {
	if (Notification.permission === 'granted') {
		return getSystemNotification(body, title);
	} else if (Notification.permission !== 'denied') {
		Notification.requestPermission().then((permission) => {
			if (permission === 'granted') {
				return getSystemNotification(body, title);
			}
		});
	}
	return void 0;
}
const taskList = new Map<String, Task>();

export function useCore(): Core {
	return {
		bus,
		showNotification: showSystemNotification,
		taskList,
	};
}
