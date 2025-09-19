// scan.ts
export default class Scan {
  private barCode: string = '';
  private lastTime: number = 0;
  private timeout: number;
  private timer: NodeJS.Timeout | null = null;
  private eventHandler: (e: KeyboardEvent) => void;

  constructor(timeout = 100) {
    this.timeout = timeout;
    this.eventHandler = this.eventListenerScanCode.bind(this);
  }

  private eventListenerScanCode(e: KeyboardEvent): void {
    const currCode = e.keyCode || e.which || e.charCode;
    const currTime = new Date().getTime();

    if (this.lastTime > 0) {
      if (currTime - this.lastTime <= this.timeout) {
        this.barCode += String.fromCharCode(currCode!);
      } else {
        this.clearBarCode();
      }
    } else {
      this.barCode = String.fromCharCode(currCode!);
    }

    // console.log(currTime, "监听到的值：", this.barCode);
    this.lastTime = currTime;

    if (currCode === 13) { // Enter键
      if (this.barCode) {
        const code = this.barCode.substring(0, this.barCode.length - 1).trim(); // 去除末尾的Enter键
        if (code) {
          this.emitScan(code);
        }
      }
      this.clearBarCode();
    }

    if (this.timer) {
      clearTimeout(this.timer);
    }
    this.timer = setTimeout(() => {
      if (this.lastTime) {
        this.clearBarCode();
        console.log("执行清空");
      }
      clearTimeout(this.timer);
    }, this.timeout);
  }

  private clearBarCode(): void {
    this.barCode = '';
    this.lastTime = 0;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }

  public start(): void {
    window.addEventListener("keypress", this.eventHandler);
  }

  public stop(): void {
    window.removeEventListener("keypress", this.eventHandler);
    this.clearBarCode();
  }

  private emitScan(code: string): void {
    this.onScanCallbacks.forEach(callback => callback(code));
  }

  private onScanCallbacks: ((code: string) => void)[] = [];

  public onScan(callback: (code: string) => void): () => void {
    this.onScanCallbacks.push(callback);
      console.log(9090)
    return () => {
      this.onScanCallbacks = this.onScanCallbacks.filter(cb => cb !== callback);
    };
  }
}