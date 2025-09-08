import subprocess
import modal

# --- 配置 ---
VOLUME_NAME = "my-notebook-volume"
APP_NAME = "interactive-app"
APP_DIR = "/app"

# --- Modal App 设置 ---
app = modal.App(APP_NAME)

# 定义环境镜像
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git")
    .pip_install(
        "torch",
        "torchvision",
        "transformers",
        "accelerate",
        "safetensors",
        "sentencepiece",
        "dashscope",
        "peft",
        "requests",
        "git+https://github.com/huggingface/diffusers.git",
    )
)

# 从统一名称创建或获取持久化存储卷
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# --- Modal 函数定义 ---

@app.function(
    image=image,
    volumes={APP_DIR: volume},
    gpu="B200",   # ✅ 这里修复了 GPU 写法
    timeout=3600,
)
def run_command_in_container(command: str):
    print(f"准备执行命令: '{command}'")
    try:
        subprocess.run(command, shell=True, check=True, cwd=APP_DIR)
        print("\n命令执行成功。")
    except subprocess.CalledProcessError as e:
        print(f"\n命令执行失败: {e}")


# --- CLI 入口点 ---

@app.local_entrypoint()
def main(command: str):
    run_command_in_container.remote(command)
