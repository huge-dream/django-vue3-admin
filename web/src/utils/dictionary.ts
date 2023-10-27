import { toRaw } from 'vue';
import { DictionaryStore } from '/@/stores/dictionary';

/**
  * @method 获取指定name字典
  */
export const dictionary = (key: string,value:string|number) => {
  const dict = DictionaryStore()
  const dictionary = toRaw(dict.data)
  if(value!==null || value !==''){
    for (let item of dictionary[key]) {
      if (item.value === value) {
        return item.label
      }
    }
    return  ''
  }
  return dictionary[key]
}
