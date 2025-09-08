import subprocess
import modal

# --- 配置 ---
VOLUME_NAME = "my-notebook-volume"
APP_NAME = "interactive-app"
APP_DIR = "/app"

# --- Modal App 设置 ---
app = modal.App(APP_NAME)

# 定义环境镜像，只安装 torch 和 diffusers
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git")  # diffusers 从 GitHub 安装需要 git
    .pip_install(
        "torch",
        "git+https://github.com/huggingface/diffusers.git",
    )
)

# 从统一名称创建或获取持久化存储卷
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# --- Modal 函数定义 ---

@app.function(
    image=image,
    volumes={APP_DIR: volume},
    gpu=modal.gpu.A100(),  # 请求 A100 GPU
    timeout=3600,  # 容器最长运行 1 小时
)
def run_command_in_container(command: str):
    """
    在容器内安全地执行终端命令。
    """
    print(f"准备执行命令: '{command}'")
    try:
        subprocess.run(command, shell=True, check=True, cwd=APP_DIR)
        print("\n命令执行成功。")
    except subprocess.CalledProcessError as e:
        print(f"\n命令执行失败: {e}")


# --- CLI 入口点 ---

@app.local_entrypoint()
def main(command: str):
    """
    本地入口函数，用于在容器中执行命令。

    使用方法:
    modal run notebook.py --command "your-command-here"
    """
    run_command_in_container.remote(command)
