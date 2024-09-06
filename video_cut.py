from tkinter import *
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import tkinter as tk
import logging
import os
import datetime
from datetime import datetime
from ttkbootstrap.dialogs import Messagebox

import subprocess
import json
from pathlib import Path
import subprocess


# 指定日志文件的绝对路径
log_dir = "C:/logs"
log_file_path = os.path.join(log_dir, "shipin-{datetime}.log")

# 确保日志目录存在
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志记录
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class VideoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("瓜爷自用剪辑软件")
        # 视频总时长
        self.video_time = None
        # 视频路径
        self.video_path = None
        # 视频信息
        self.video_info = ""
        # 剪切开始时间临时存放
        self.start_time = "00:00:00"
        # 剪切结束时间临时存放
        self.end_time = "00:00:00"
        # 剪切时间段存储列表
        self.cut_list = []
        self.cut_list_time = None
        # 剪切文件路径
        self.temp_file_list = []
        # 剪切文件存放目录
        self.video_cut_temp_folder = ""
        # 截取时间点击标识符
        self.click_count = 0
        # 当前获取的时长
        self.current_time = 0

        # 选择文件
        self.select_file_button = ttk.Button(
            self.root, text="选择视频文件", command=self.select_file
        )
        self.select_file_button.pack(anchor="center", pady=20)
        self.select_file_button_path_show = ttk.Label(
            self.root, text="未选择视频", font=("仿宋", 12)
        )
        self.select_file_button_path_show.pack(anchor="center")
        self.select_file_button_path_show1 = ttk.Label(
            self.root, text="", font=("仿宋", 12)
        )
        self.select_file_button_path_show1.pack(anchor="center")
        self.video_info_text = ttk.Label(
            self.root, text="视频信息：", font=("仿宋", 12)
        )
        self.video_info_text.pack(anchor="center")
        self.video_info_text1 = ttk.Label(self.root, text="", font=("仿宋", 12))
        self.video_info_text1.pack(anchor="center")

        # 设置Scale
        self.scale = ttk.Scale(
            self.root,
            from_=0,
            to=self.video_time,
            orient="horizontal",
            variable=self.cut_list_time,
        )
        self.scale.pack(fill="x", pady=20)
        
        # 获取时间
        self.get_time_button = ttk.Button(
            self.root, text="获取时间", command=self.get_time
        )
        self.get_time_button.pack(pady=10)
        # 预览
        self.preview_button = ttk.Button(self.root, text="预览", command=self.preview_video)
        self.preview_button.pack(pady=10)
    


        # 创建一个Label来显示实时滚动的值
        self.current_value_label2 = ttk.Label(
            self.root, text="当前获取的时间：", font=("仿宋", 12)
        )
        self.current_value_label2.pack()
        self.current_value_label = ttk.Label(
            self.root, text="00:00:00", font=("仿宋", 12)
        )
        self.current_value_label.pack(anchor="center")

        # 片段截取 开始时间
        self.current_start_time_value_label = ttk.Label(
            self.root, text=f"开始时间：{self.start_time}", font=("仿宋", 12)
        )
        self.current_start_time_value_label.pack()
        # 片段截取 结束时间
        self.current_end_time_value_label = ttk.Label(
            self.root, text=f"结束时间：{self.end_time}", font=("仿宋", 12)
        )
        self.current_end_time_value_label.pack()
        # 片段列表
        self.cut_list_time = ttk.Label(self.root, text=f"片段列表", font=("仿宋", 12))
        self.cut_list_time.pack()
        self.cut_list_show = ttk.ScrolledText(
            self.root,
            font=("仿宋", 12),
            height=10,
            width=60,)
        self.cut_list_show.pack()

        # 剪切按钮
        self.get_time_button = ttk.Button(
            self.root, text="剪切", command=self.cut_video
        )
        self.get_time_button.pack(pady=10)

    def select_file(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("视频文件", "*.mp4 *.avi *.mkv *.gif")]
        )
        if self.video_path is None or self.video_path == "":
            self.select_file_button_path_show.config(text="请重新选择文件")
            logging.info(f"未选择视频文件")
        else:
            self.select_file_button_path_show.config(text=f"已选择视频文件：")
            self.select_file_button_path_show.pack(anchor="center")
            # 获取视频信息
            video_info = self.getvideo_info(self.video_path)
            # ffmpeg获取视频时长
            # video_info = self.video_time_length()

            if video_info:
                size =int( video_info.get("format", []).get("size"))
                for suffix in ['B', 'KB', 'MB', 'GB', 'TB']:  # 定义各单位
                    if size < 1024.0 or suffix == 'TB':  # 如果size小于1024或已经是TB级别，则退出循环
                        break
                    size /= 1024.0  # 将size转换为下一单位
                format_size =  f"{size:.2f} {suffix}"  # 返回格式化后的文件大小字符串
                 
                format_name = video_info.get("format", []).get("format_name")

                for strems in  video_info.get("streams"):
                    if strems.get("codec_type", {}) == "video":
                        width = strems.get("width", 0)
                        height = strems.get("height", 0)
                        codec_name = strems.get("codec_name", 0)
                        video_length = float(
                            strems.get("duration", 0)
                        )
                        self.video_time = int(video_length)
                        info_text = (
                            f"时长: {str(int(video_length / 3600)).__add__('小时').__add__(str(int(video_length % 3600 / 60))).__add__('分钟').__add__(str(int(video_length % 60))).__add__('秒')},\n"
                            f"分辨率: {width}×{height},\n"
                            f"编码器名称: {codec_name},\n"
                            f"视频格式: {format_name},\n"
                            f"视频大小: {format_size}"
                        )
                        self.video_info_text1.config(text=info_text)
                        break
                logging.info(f"视频信息: {video_info}")
                if self.video_time is not None or 0:
                    logging.info(f"ffmpeg获取时长命令成功")
                else:
                    logging.info(f"ffmpeg获取时长命令失败")
                # 刷新视频时长
                self.scale.config(to=self.video_time)
                # 绑定鼠标滚轮事件
                self.scale.bind("<MouseWheel>", self.on_mouse_wheel)
                # 绑定点击和拖动事件
                self.scale.bind("<ButtonRelease-1>", self.get_scale_value)
                # 鼠标左键释放时获取值
                self.scale.bind("<B1-Motion>", self.get_scale_value)
                self.select_file_button_path_show1.config(
                    text=f"{self.video_path}", wraplength=600
                )
                self.select_file_button_path_show1.pack(anchor="center")

    # 获取视频时长并格式化输出
    def video_time_length(self):
        """
        获取视频时长并格式化输出
        :return: 格式化的时长字符串（小时和分钟）
        """
        v_format = self.video_info["format"]  # 获取视频的格式信息
        duration = float(v_format["duration"])  # 获取视频时长（秒）
        # 计算小时和分钟，并返回格式化的字符串
        return (
            str(int(duration / 3600))
            .__add__("小时")
            .__add__(str(int(duration % 3600 / 60)))
            .__add__("分钟")
        )
    

    


    # 获取视频信息
    def getvideo_info(self, filepath):
        """
        解析视频文件，获取视频的基本信息
        :param filepath: 视频文件路径
        """
        # 设置视频文件路径
        try:
            # 使用subprocess调用ffprobe命令获取视频信息，结果输出为JSON格式
            res = subprocess.check_output(
                [
                    "ffprobe",
                    "-i",
                    filepath,
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    "-v",
                    "quiet",
                ]
            )
            res = res.decode("utf8")  # 将字节流转换为UTF-8编码的字符串
            self.video_info = json.loads(res)  # 将JSON字符串转换为Python字典并保存
            # 格式化json
            # formatted_json = json.dumps(self.video_info, indent=4, ensure_ascii=False)
            # 打印 json
            # print(formatted_json)
            return self.video_info
        except (TypeError, ValueError) as e:
            return f"JSON 格式化失败: {e}"
        except Exception as e:
            # 如果ffprobe命令执行失败，则捕获异常并打印错误信息
            logging.info(e)
            raise Exception("获取视频信息失败")  # 抛出自定义异常，提示获取视频信息失败

    # 格式化时间
    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        hours_str = str(int(hours)) if hours >= 10 else "0" + str(int(hours))
        minutes_str = str(int(minutes)) if minutes >= 10 else "0" + str(int(minutes))
        seconds_str = str(int(seconds)) if seconds >= 10 else "0" + str(int(seconds))
        return f"{hours_str}:{minutes_str}:{seconds_str}"

    def on_mouse_wheel(self, event):
        # 获取滚轮滚动的方向和量
        delta = -1 * (event.delta / 120)
        current_value = self.scale.get()
        new_value = current_value + delta * 12  # 每次滚动改变12秒

        # 确保新值在范围内
        new_value = max(0, min(new_value, self.video_time))
        self.scale.set(new_value)
        formatted_time = self.format_time(new_value)
        self.current_value_label.config(text=str(f"{formatted_time}"))

    def get_scale_value(self, event):
        # 使用Scale的get()方法获取当前值
        value = self.scale.get()
        self.scale.set(value)
        formatted_time = self.format_time(value)
        self.current_value_label.config(text=str(f"{formatted_time}"))

    def get_time(self):
        # 判断是否导入文件
        if not self.video_path:
            Messagebox.show_warning(title="错误 ", message="未选择视频文件")
            logging.warning("未选择视频文件")
            return
        # 点击次数
        self.click_count += 1
        self.current_time = int(self.scale.get())

        # 点击次数为奇数数时，获取开始时间
        if self.click_count % 2 == 1:
            self.start_time = self.format_time(self.current_time)
            self.current_start_time_value_label.config(
                text=f"开始时间：{self.start_time}"
            )
            self.current_end_time_value_label.config(text=f"结束时间：{self.end_time}")

        else:  # 点击次数为偶数时，获取结束时间
            # 将字符串转换为datetime对象
            self.end_time = self.format_time(self.current_time)
            time1 = datetime.strptime(self.start_time, "%H:%M:%S")
            time2 = datetime.strptime(self.end_time, "%H:%M:%S")
            if time2 <= time1:
                # 重置片段时间组
                self.start_time = "00:00:00"
                self.end_time = "00:00:00"
                self.current_start_time_value_label.config(
                    text=f"开始时间：{self.start_time}"
                )
                self.current_end_time_value_label.config(
                    text=f"结束时间：{self.end_time}"
                )
                self.click_count = 0
                Messagebox.show_warning(
                    "时间选择错误", "结束时间小于开始时间，请重新从开始时间添加时间片段"
                )
                logging.warning("时间选择不合理")
                return
            self.current_end_time_value_label.config(text=f"结束时间：{self.end_time}")
            self.cut_list.append((self.start_time, self.end_time))

            # 并存储时间
            self.cut_list_show.insert(
                "end",
                f"片段{len(self.cut_list)}：{self.start_time} - {self.end_time}\n",
            )
            # 重置片段时间组
            self.start_time = "00:00:00"
            self.end_time = "00:00:00"
            # 刷新剪切列表
            # 检查是否至少有一行文本
            end_index = self.cut_list_show.index("end")
            if end_index != "1.0":  # "1.0" 表示第一行第一个字符的位置，即文本的开始
                self.cut_list_show.delete("1.0", end_index)
            else:
                self.cut_list_show.delete("1.0", "end")

            formatted_str = "\n".join(
                [
                    f"片段{i+1}：{start}-{end}"
                    for i, (start, end) in enumerate(self.cut_list)
                ]
            )
            self.cut_list_show.insert("end", formatted_str)

    # 剪切视频
    def cut_video(self):
        # 检查是否导入文件
        if not self.video_path:
            Messagebox.show_warning(itle='"错误" ', message="未选择视频文件")
            logging.warning("未选择视频文件")
            return

        # 检查是否至少有一个片段
        if not self.cut_list:
            Messagebox.show_warning(title="未选择片段错误 ",message="片段不完整，或没有开始时间，或没有结束时间，请重新选择片段")
            logging.warning("没有选择片段")
            return
        # 生成临时文件夹,以文件名为文件夹名
        # 文件名带后缀
        file_name_with_extension = Path(self.video_path).name
        # 文件名
        file_name = Path(self.video_path).stem
        # 文件后缀
        file_extension = Path(self.video_path).suffix
        self.video_suffix = file_extension
        temp_folder = Path(self.video_path).parent / file_name
        self.video_cut_temp_folder = temp_folder
        # 检查文件夹是否存在
        if not temp_folder.exists():
            # 如果不存在，创建文件夹
            temp_folder.mkdir()
            logging.info(f"文件夹 '{temp_folder}' 已创建。")
        else:
            logging.info(f"文件夹 '{temp_folder}' 已存在。")
        # 生成剪切文件名
        for cut_file in self.cut_list:
            logging.info(f"剪切片段：{cut_file}")
            # 剪切文件名
            cut_file_name = (
                file_name + "xxx" + cut_file[0].replace(":","-") + "--" + cut_file[1].replace(":","-") + file_extension
            )
            # 剪切文件路径
            cut_file_path = Path(temp_folder) / cut_file_name

            logging.info(f"剪切文件路径：{cut_file_path}")
            # 添加到合并路径列表
            self.temp_file_list.append(cut_file_path)

            # 调用ffmpeg命令进行剪切
            # 构建ffmpeg命令
            ffmpeg_command = [
                'ffmpeg',
                '-i', self.video_path,      # 输入文件
                '-ss', cut_file[0],         # 剪切开始时间
                '-to', cut_file[1],         # 剪切结束时间
                '-c', 'copy',               # 复制编解码器，不重新编码
                cut_file_path               # 输出文件
            ]
            logging.info(f"ffmpeg命令：{ffmpeg_command}")
            # 运行ffmpeg命令
            try:
                result = subprocess.run(ffmpeg_command, check=True)
                Messagebox.ok(title="完成", message=f"视频剪切完成，剪切的视频文件路径：{result}")
                logging.info(f"视频剪切成功，输出文件：{cut_file_path}")
            except subprocess.CalledProcessError as e:
                Messagebox.show_error(title="错误", message=f"视频剪切失败，错误片段{e}")
                logging.info(f"剪切视频时出错：错误片段{cut_file[0]}--{cut_file[1]}")
                logging.info(f"剪切视频时出错：{e}")
                return 

        Messagebox.show_info(title="完成", message=f"视频剪切完成，剪切的视频文件路径：{self.video_cut_temp_folder}")

    # 预览
    def preview_video(self):
        if self.current_time >=5 :
            start_time = self.format_time(self.current_time-5)
        else:
            start_time = self.format_time(0)
        if self.video_time-5 <= self.current_time:
            end_time = self.format_time(self.video_time)
        else:
            end_time = self.format_time(self.current_time+5)

    
        gif_command = [
        'ffmpeg',
        '-i',Path(self.video_path),
        '-ss', start_time,
        '-to', end_time,
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-filter:v', f"fps=10,scale=320:-1:flags=lanczos [x]; [x][1:v] paletteuse",
        '-f', 'gif',
        Path(self.video_cut_temp_folder) / "preview.gif"
    ]


def center_window(width, height):
    # 获取屏幕的宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口居中的位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # 设置窗口位置
    root.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":

    root = ttk.Window(themename="darkly")
    # 设置窗口的标题
    root.title("瓜爷自用剪辑软件")
    style = ttk.Style("darkly")
    ttk.Sizegrip(root, bootstyle="info").pack(side="right", anchor="se")
    center_window(1000, 900)

    # 设置窗口的图标
    # root.iconbitmap(r"c:\Users\Rinhon\Desktop\python_script\media.ico")
    # root.iconbitmap(f"media.ico")
    root.iconbitmap(f"f:\workspace\电影票.ico")

    # 设定是否能够改变窗口的宽和高尺寸
    root.resizable(width=True, height=True)
    # 设定窗口的背景颜色
    # root.config(backgroundImage=r'c:\Users\Administrator\Pictures\Screenshots\d265a364622d70cc653638c6ec268c05.jpg')
    # 创建 Guidemo 类的实例并传递 root 作为参数
    guidemo_instance = VideoEditor(root)

    # 显示窗口
    root.mainloop()
