Flash
=====

### Setting up ESP-IDF and the build environment

```shell
mkdir uiflow_workspace && cd uiflow_workspace
git clone -b uiflow/v2.0-idf5.0.4 https://github.com/m5stack/esp-idf.git 
git -C esp-idf submodule update --init --recursive
./esp-idf/install.sh
. ./esp-idf/export.sh
```

### Building the firmware

```shell
git clone https://github.com/m5stack/uiflow_micropython
cd uiflow_micropython/m5stack
```

- 在CmakeLists.txt文件LVGL部分后的include调整到前面`include($ENV{IDF_PATH}/tools/cmake/project.cmake)`  # todo 后续提交更新后可以删除。
- 在m5stack/CMakeListsLvgl.cmake中，将 adcblock 改为 adc_block
- 引入`#include "sdkconfig.h"`

```shell
make BOARD=M5STACK_CoreS3 BOARD_TYPE=cores3 submodules
make BOARD=M5STACK_CoreS3 BOARD_TYPE=cores3 patch
make BOARD=M5STACK_CoreS3 BOARD_TYPE=cores3 littlefs
make BOARD=M5STACK_CoreS3 BOARD_TYPE=cores3 mpy-cross
make BOARD=M5STACK_CoreS3 BOARD_TYPE=cores3 menu  # 将tinyusb配置中的HID设置为1.
make BOARD=M5STACK_CoreS3 BOARD_TYPE=cores3 PORT=/dev/ttyACM0 flash_all
```


### 设置启动键盘为default启动选项(目前已经默认为这样)

```shell
# 烧写后

# 使用minicorn等串口工具连接到python shell
minicom -D /dev/ttyACM0

# 进入后会卡在主线程中。按Ctrl-c两次，停止python正在执行的内容，返回shell，会显示>>>。

# 输入如下python指令，将之后的启动设置为从main.py启动，这样就会直接启动coopboard的主循环。
import esp32
nvs = esp32.NVS("uiflow")
nvs.set_u8("boot_option", 0)

# 重启，按reset按键
```


开发查看
======

### 手动执行mpy中的代码

```python
from coopboardpy.run import Runner
Runner().main_loop()
```


### 如何设置hid cdc符合设备
- 明确调用关系
    - 注册配置符 micropython/ports/esp32/usb.c
    - 
- 需要配置sdkconfig，增加tinyusb的hid配置
    - `make BOARD=M5STACK_CoreS3 BOARD_TYPE=cores3 PORT=/dev/ttyACM0 menu` 将tinyusb配置中的HID设置为1.


### 如何增加I2C通信模块和PCA9555模块


```
git submodule add https://github.com/Nicolai-Electronics/esp32-component-i2c-pca9555.git m5stack/components/i2c_pca9555
git submodule add https://github.com/Nicolai-Electronics/esp32-component-bus-i2c.git m5stack/components/bus_i2c
```

### 使用patch方式修改子模块中的代码


