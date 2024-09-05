import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import shutil
import json
import tkinter as tk
from ttkbootstrap import Style
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# 指定日志文件的绝对路径
log_dir = "C:/logs"
log_file_path = os.path.join(log_dir, "shipin.log")

# 确保日志目录存在
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志记录
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class VideoClipper:
    def __init__(self, root):
        self.root = root
        self.root.title("视频剪切与合并")
        self.clips = []  # 用于存储时间片段的列表
        self.temp_path = ''

        # 设置 ttkbootstrap 样式
        style = Style(theme='darkly')

        # 添加选择视频文件的按钮
        self.btn_select_video = tk.Button(
            root, text="选择视频文件", command=self.select_video)
        self.btn_select_video.pack()

        # 显示选定的视频文件路径的标签，并设置wraplength以便长文本换行
        self.video_path_label = tk.Label(
            root, text="未选择视频文件", wraplength=400, anchor='w')
        self.video_path_label.pack(fill='x')

        # 显示视频参数信息的标签
        self.video_info_text = tk.Label(
            root, text='参数', wraplength=400, anchor='w')
        self.video_info_text.pack(fill='both')

        # 添加开始时间和结束时间的下拉框
        self.start_time_frame = tk.Frame(root)
        self.start_time_frame.pack()
        self.end_time_frame = tk.Frame(root)
        self.end_time_frame.pack()

        # 创建开始时间的时、分、秒下拉框
        self.start_hour = self.create_time_dropdown(
            self.start_time_frame, 0, 24, "时")
        self.start_minute = self.create_time_dropdown(
            self.start_time_frame, 0, 60, "分")
        self.start_second = self.create_time_dropdown(
            self.start_time_frame, 0, 60, "秒")

        # 创建结束时间的时、分、秒下拉框
        self.end_hour = self.create_time_dropdown(
            self.end_time_frame, 0, 24, "时")
        self.end_minute = self.create_time_dropdown(
            self.end_time_frame, 0, 60, "分")
        self.end_second = self.create_time_dropdown(
            self.end_time_frame, 0, 60, "秒")

        # 用于显示时间片段的列表框
        self.clip_listbox = tk.Listbox(root, height=5, width=50)
        self.clip_listbox.pack()

        # 复制到剪切板按钮
        self.btn_copy_to_clipboard = tk.Button(
            root, text="复制时间片段到剪切板", command=self.copy_clips_to_clipboard)
        self.btn_copy_to_clipboard.pack()

        # 从剪切板导入按钮
        self.btn_import_from_clipboard = tk.Button(
            root, text="从剪切板导入时间片段", command=self.import_clips_from_clipboard)
        self.btn_import_from_clipboard.pack()

        # 剪切按钮
        self.btn_cut_clips = tk.Button(
            root, text="剪切", command=self.cut_video)
        self.btn_cut_clips.pack()

        # # 合并按钮
        # self.btn_merge_clips = tk.Button(
        #     root, text="合并", command=self.merge_clips)
        # self.btn_merge_clips.pack()

    # 创建时间选择的下拉框
    def create_time_dropdown(self, parent, start, end, label_text):
        label = tk.Label(parent, text=label_text)
        label.pack(side=tk.LEFT)  # 添加时间单位的标签（时、分、秒）

        var = tk.StringVar(parent)

        # 创建只读的下拉框，范围从start到end
        dropdown = ttk.Combobox(parent, textvariable=var, values=[
                                f"{i:02}" for i in range(start, end)], state="readonly")

        # 设置下拉框的宽度为20像素
        dropdown.config(width=5)
        dropdown.set("00")
        dropdown.pack(side=tk.LEFT)
        return dropdown

    # 选择视频文件的回调函数
    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            title="选择视频文件", filetypes=[("MP4文件", "*.mp4"), ("MKV文件", "*.mkv")])
        self.video_path_label.config(
            text=self.video_path)  # 在标签中显示视频文件路径

        if not self.video_path:
            messagebox.showerror("错误", "未选择视频文件")
            logging.warning("未选择视频文件")
        else:
            video_path = self.video_path  # 在标签中显示视频文件路径
            logging.info(f"选择了视频文件: {self.video_path}")

            # 获取并显示视频信息
            video_info = self.getvideo_info(self.video_path)
            if video_info:
                # 处理比特率的转换
                # bit_rate = float(video_info.get('bit_rate', '0'))/8
                width = video_info.get("streams", [])[0].get("width", 0)
                height = video_info.get("streams", [])[0].get("height", 0)
                format_name = video_info.get("streams", [])[
                    0].get("format_name", 0)
                codec_name = video_info.get("streams", [])[
                    0].get("codec_name", 0)

                info_text = f"时长: {21}, \n" \
                            f"分辨率: {width}x{height},\n " \
                            f"编码器名称: {codec_name},\n" \
                            f"编码器名称: {video_info.get('codec_name', '未知')},\n" \
                            f"视频格式: {format_name}"

                # f"平均码率: {bit_rate} kbps" \
                # self.video_info_text.delete(1.0, tk.END)  # 清空文本框
                # self.video_info_text.insert(tk.END, video_info)  # 插入视频信息
                self.video_info_text.config(text=info_text)
                logging.info(f"视频信息: {video_info}")
            else:
                self.video_info_text.config(text="无法获取视频信息")
                logging.error("无法获取视频信息")
    # 添加时间片段

    def add_clip(self):
        # 获取开始时间和结束时间
        start = f"{self.start_hour.get()}:{self.start_minute.get()}:{self.start_second.get()}"
        end = f"{self.end_hour.get()}:{self.end_minute.get()}:{self.end_second.get()}"
        # 校验起始时间必须小于结束时间
        if start >= end:
            messagebox.showerror("错误", "起始时间必须小于结束时间")
            logging.warning(f"添加时间片段失败，起始时间{start}不小于结束时间{end}")
            return

        # 将片段添加到列表中并排序
        self.clips.append((start, end))
        self.clips.sort()
        self.update_clip_listbox()  # 更新列表框，显示所有添加的片段
        logging.info(f"添加了时间片段: {start} 到 {end}")

    # 复制时间片段到剪切板
    def copy_clips_to_clipboard(self):
        clips_text = "\n".join(
            [f"{start} - {end}" for start, end in self.clips])
        self.root.clipboard_clear()
        self.root.clipboard_append(clips_text)
        logging.info("时间片段已复制到剪切板")

    # 从剪切板导入时间片段
    def import_clips_from_clipboard(self):
        clipboard_text = self.root.clipboard_get()
        imported_clips = []
        try:
            for line in clipboard_text.splitlines():
                start, end = line.split(" - ")
                imported_clips.append((start, end))
            self.clips = imported_clips
            self.update_clip_listbox()
            logging.info("时间片段已从剪切板导入")
        except Exception as e:
            messagebox.showerror("错误", "剪切板内容格式不正确")
            logging.error(f"从剪切板导入时间片段时出错: {e}")

    # 剪切视频
    def cut_video(self):
        if not os.path.isfile(self.video_path):
            messagebox.showerror("错误", "视频文件不存在")
            logging.error("视频文件不存在，无法合并")
            return None

        # 创建存放剪切片段的新文件夹
        # 获取视频文件所在目录
        directory = os.path.dirname(self.video_path)
        print('directory = '+directory)

        # 获取视频文件名（不带扩展名）
        folder_name = os.path.splitext(self.video_path)
        print('folder_name = '+folder_name[0])

        # 创建新的文件夹路径
        new_folder_path = os.path.join(directory,  folder_name[0])
        print('new_folder_path = '+new_folder_path)

        # 创建文件夹（如果不存在）
        os.makedirs(new_folder_path, exist_ok=True)

        logging.info(f"创建了文件夹: {new_folder_path}")
        output_folder = new_folder_path
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"创建了输出文件夹: {output_folder}")

        filelist = []
        for i, (start, end) in enumerate(self.clips):
            # 生成每个剪切片段的输出文件路径
            output_clip = output_folder + '/' + f"clip_{i}.mp4"
            filelist.append(output_clip)
            try:
                # 调用clip_video函数剪切视频片段
                self.clip_video(self.video_path, output_clip, start, end)
                # 将片段文件路径写入文件列表

            except Exception as e:
                messagebox.showerror("错误", f"剪切片段时出错: {e}")
                logging.error(f"剪切片段时出错: {e}")
                # shutil.rmtree(filelist)  # 删除临时文件列表
                return None

    # 剪切视频用方法
    def clip_video(self, video_path, output_clip, start, end):
        # 使用ffmpeg命令剪切视频
        command = [
            'ffmpeg',
            '-i', video_path,
            '-ss', start,
            '-to', end,
            '-c', 'copy',
            output_clip
        ]
        try:
            # 捕获标准输出和标准错误，输出到控制台以便排查问题
            result = subprocess.run(
                command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"剪切了视频片段: {start} 到 {end}，输出文件: {output_clip}")
        except subprocess.CalledProcessError as e:
            # 打印和记录标准输出和错误信息
            logging.error(f"ffmpeg 命令执行失败: {e}")
            logging.error(f"命令: {' '.join(command)}")
            logging.error(f"返回码: {e.returncode}")
            logging.error(f"标准输出: {e.stdout.decode()}")
            logging.error(f"标准错误: {e.stderr.decode()}")
            raise  # 继续抛出异常，以便在调用此函数的地方进行处理

        # 创建存放剪切片段的新文件夹
        # 获取视频文件所在目录
        directory = os.path.dirname(self.video_path)
        print('directory = '+directory)

        # 获取视频文件名（不带扩展名）
        folder_name = os.path.splitext(self.video_path)
        print('folder_name = '+folder_name[0])

        # 创建新的文件夹路径
        new_folder_path = os.path.join(directory,  folder_name[0])
        print('new_folder_path = '+new_folder_path)

        # 创建文件夹（如果不存在）
        os.makedirs(new_folder_path, exist_ok=True)

        logging.info(f"创建了文件夹: {new_folder_path}")
        output_folder = new_folder_path
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"创建了输出文件夹: {output_folder}")

    # 获取视频信息
    def getvideo_info(self, filepath):
        """
        解析视频文件，获取视频的基本信息
        :param filepath: 视频文件路径
        """
        self.filepath = filepath  # 设置视频文件路径
        try:
            # 使用subprocess调用ffprobe命令获取视频信息，结果输出为JSON格式
            res = subprocess.check_output(
                ['ffprobe', '-i', self.filepath, '-print_format', 'json',
                    '-show_format', '-show_streams', '-v', 'quiet']
            )
            res = res.decode('utf8')  # 将字节流转换为UTF-8编码的字符串
            self.video_info = json.loads(res)  # 将JSON字符串转换为Python字典并保存

            formatted_json = json.dumps(
                self.video_info, indent=4, ensure_ascii=False)
            return self.video_info
        except (TypeError, ValueError) as e:
            return f"JSON 格式化失败: {e}"

        except Exception as e:
            # 如果ffprobe命令执行失败，则捕获异常并打印错误信息
            print(e)
            raise Exception('获取视频信息失败')  # 抛出自定义异常，提示获取视频信息失败

    # 获取视频的宽度和高度
    def video_width_height(self):
        """
        获取视频的宽度和高度
        :return: (width, height) 元组
        """
        streams = self.video_info['streams'][0]  # 获取视频流的第一个元素（通常是视频流）
        return (streams['width'], streams['height'])  # 返回视频的宽度和高度

    # 获取视频文件大小，并按指定单位格式化输出
    def video_filesize(self, format='gb'):
        """
        获取视频文件大小，并按指定单位格式化输出
        :param format: 格式化单位（默认：GB）
        :return: 格式化后的视频大小字符串
        """
        v_format = self.video_info['format']  # 获取视频的格式信息
        size = int(v_format['size'])  # 获取视频文件的大小（字节）

        # 定义单位换算
        kb = 1024
        mb = kb * 1024
        gb = mb * 1024
        tb = gb * 1024

        # 根据视频大小返回对应的格式化字符串
        if size >= tb:
            return "%.1f TB" % float(size / tb)
        if size >= gb:
            return "%.1f GB" % float(size / gb)
        if size >= mb:
            return "%.1f MB" % float(size / mb)
        if size >= kb:
            return "%.1f KB" % float(size / kb)

    # 获取视频的总帧数
    def video_full_frame(self):
        """
        获取视频的总帧数
        :return: 总帧数
        """
        stream = self.video_info['streams'][0]  # 获取视频流的第一个元素
        return stream['nb_frames']  # 返回视频的帧数

    # 获取视频时长并格式化输出
    def video_time_length(self):
        """
        获取视频时长并格式化输出
        :return: 格式化的时长字符串（小时和分钟）
        """
        v_format = self.video_info['format']  # 获取视频的格式信息
        duration = float(v_format['duration'])  # 获取视频时长（秒）
        # 计算小时和分钟，并返回格式化的字符串
        return str(int(duration / 3600)).__add__('小时').__add__(str(int(duration % 3600 / 60))).__add__('分钟')

    # 获取视频的基本信息并返回一个字典
    def video_info(self):
        """
        获取视频的基本信息并返回一个字典
        :return: 包含路径、分辨率、文件大小和时长的字典
        """
        item = {
            'path': self.filepath,  # 视频路径
            'height_width': self.video_width_height(),  # 视频分辨率（宽度和高度）
            'filesize': self.video_filesize(),  # 视频文件大小
            'time_length': self.video_time_length()  # 视频时长
        }
        print('item = ', item)  # 打印视频信息字典
        return item  # 返回视频信息字典


# 居中窗口
def center_window(root, width, height):
    # 获取屏幕的宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口居中的位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # 设置窗口的几何参数
    root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


# 创建主窗口
root = tk.Tk()
app = VideoClipper(root)

# 设置窗口的初始尺寸
window_width = 400
window_height = 800

# 调用函数使窗口居中
center_window(root, window_width, window_height)

root.mainloop()
