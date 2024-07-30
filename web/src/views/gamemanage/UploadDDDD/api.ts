// 将文件传到后端
import { request } from '/@/utils/service';

export const apiPrefix = 'api/game_manage/upload_dddd/';

export function UploadDDDD(obj: any) {
    return request({
        url: apiPrefix,
        method: 'post',
        data: obj,
    });
}
