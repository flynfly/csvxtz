# DelsysAPI Python 示例

这是一个使用 DelsysAPI AeroPy 层的示例 Python GUI 应用程序，演示了用户可以在自己的代码中实现的功能。此示例允许用户连接到基站，配对新传感器，扫描已配对传感器，然后通过绘图显示 EMG 数据。

此版本已在 [Python 3.8.1](https://www.python.org/downloads/release/python-381/) 上进行了测试。

查看 [AeroPy 文档](#AeroPy-文档) 

## 入门
1. 安装 Python：[Python 3.8.1](https://www.python.org/downloads/release/python-381/)。
2. 导航到 `Example-Applications/Python` 基本目录
3. 使用 `python -m pip install -r requirements.txt` 安装依赖项
-注意：PythonNet 库仅支持到 python 3.8。
4. 打开 `/AeroPy/TrignoBase.py` 并复制/粘贴 Delsys Inc. 在购买系统期间提供的密钥/许可证字符串。如果遇到任何问题，请联系 [支持](https://delsys.com/support/)。
5. 如果您使用的是 IDE，请从设置中设置 Python 解释器/虚拟环境。
6. 确保 Trigno 基站或 Lite 已插入，然后运行 `DelsysPythonDemo.py`


## 使用说明
单击开始菜单上的 `Collect Data` 按钮以打开数据收集窗口。

确保您的 Trigno 系统已连接到电源和 PC 通过 USB。单击 `Connect` 按钮将应用程序连接到基站。在终端中，您将看到一些日志和初始化消息。

通过从充电站取出并引入磁铁来打开传感器。为方便起见，充电站内置了一个磁铁，位于盒子中央的 "lock" 符号下方。如果传感器尚未与基站配对，单击 `Pair` 按钮并再次引入磁铁以启动配对。

单击 `Scan` 按钮。这将将传感器添加到应用程序的传感器列表中。通过单击它来突出显示传感器，然后从模式下拉菜单中选择其模式。设置模式是针对单个传感器完成的，而不是所有传感器。如果您希望所有传感器都具有相同的模式，可以修改代码以实现此目的。有关更多详细信息，请参阅 [AeroPy 文档](#AeroPy-文档)。

要开始数据流和绘图，请单击 `Start` 按钮。要停止数据流和绘图，请单击 `Stop` 按钮。

单击 `Reset Pipeline` 按钮以返回已连接的管道状态。注意：如果您想要在数据流后扫描/配对/更改模式，您必须单击重置管道。如果您使用相同的传感器配置进行其他数据流，可以连续按下 Start/Stop 而无需重置。

## 进一步参考
请参阅 DelsysAPI 文档 [这里](http://data.delsys.com/DelsysServicePortal/api/web-api/index.html)。


&nbsp;<br>

# AeroPy 文档

DelsysAPI 和 AeroPy 软件是与 Trigno 无线生物反馈系统一起使用的开发工具。DelsysAPI 不是用于执行评估或诊断程序。它旨在用作第三方软件应用程序的软件组件。API 的功能是管理从 Trigno 系统传输数据到第三方软件应用程序，并专为 Trigno 系统设计。AeroPy 是 DelsysAPI 的简化层，便于配置和从传感器流式传输。请参阅以下 AeroPy 命令列表。

## 设置 (python)

`DelsysAPI.dll` 必须位于项目文件夹内，例如 resources/

```python
"""
此类创建 Trigno 基站的实例。将您的密钥和许可证放在这里。
"""
import clr
clr.AddReference("/resources/DelsysAPI")
clr.AddReference("System.Collections")

from Aero import AeroPy

key = ""
license = ""

class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()
```

```python
base = TrignoBase()
TrigBase = base.BaseInstance
```
从程序脚本调用 TrignoBase 类。

```python
    def Connect_Callback(self):
        """连接到基站的回调"""
        TrigBase.ValidateBase(key, license)
```
使用 TrigBase 变量调用 AeroPy 函数。请参阅以下所有 AeroPy 方法：

### 连接到 Trigno Base/Lite
```C#
public void ValidateBase(string key, string license)
```
首次调用 Trigno Base。使用用户的密钥和许可证字符串设置与基站的连接。

&nbsp;<br>

### 传感器管理
```C#
public Task ScanSensors()
```
扫描先前配对的传感器 (RF)。
管道必须处于关闭或连接状态才能运行此命令

&nbsp;<br>  
```C#
public void PairSensor()
```
将基站设置为配对模式，允许用户将新传感器配对到基站。
管道必须处于关闭或连接状态才能运行此命令

&nbsp;<br>  
```C#
public bool SelectAllSensors()
```
选择在扫描中找到的所有传感器。如果您只想选择特定传感器，请使用 SelectSensor 方法

&nbsp;<br>  

```C#
public void SelectSensor(int sensorNum)
```
选择位于索引 `sensorNum` 的传感器进行流式传输。使用 SelectAllSensors() 方法选择所有扫描到的传感器。

&nbsp;<br>  
```C#
public SensorTrignoRf GetSensorObject(int sensorNo)
```
获取索引为 sensorNo 的传感器的传感器对象

&nbsp;<br>  
```C#
public List<string> GetAllSampleModes()
```
获取当前传感器设置的所有采样模式。

&nbsp;<br>  

```C#
public void SetSampleMode(int componentNum, string sampleMode)
```
设置给定传感器的采样模式。将索引为 componentNum 的传感器设置为 sampleMode 提供的模式。

&nbsp;<br>  
```C#
public string[] GetSensorNames()
```
返回扫描中找到的当前传感器名称的字符串数组。

&nbsp;<br>  
```C#
public string[] AvailibleSensorModes(int sensorSelected)
```
返回传感器在 sensorSelected 索引处可用的传感器模式列表。

&nbsp;<br>  

### 传感器配置（RF）

```C#
public void Configure()
```
默认配置方法 - 将为所有扫描到的传感器配置原始数据输出的管道。管道必须处于关闭或连接状态。管道将转换为已布防

&nbsp;<br>  

### 数据收集管理（RF）

```C#
public void Start()
```
启动数据流 - 管道必须处于已布防状态。管道将转换为运行

&nbsp;<br>  
```C#
public bool CheckDataQueue()
```
在运行状态（实时数据收集）中调用。如果内部数据缓冲区中有新数据准备好提取，则返回 true。如果为真，请使用 `PollData()` 返回数据结构。

&nbsp;<br>  

```C#
public Dictionary<Guid, List<double>> PollData()
```
在调用 `Start()` 方法后，此方法从数据缓冲区检索数据。每次调用此方法时，它将返回数据，然后清除内部数据队列。返回类型是字典输出，其中通道 GUID 是键，通道数据是值。

&nbsp;<br>  
```C#
public void Stop()
```
停止数据流 - 管道必须处于运行状态。管道将转换为已布防

&nbsp;<br>  
```C#
public void ResetPipeline()
```
重置（解除布防）管道 - 管道必须处于已布防状态。管道将转换为连接（允许用户在收集停止后调用 Scan/Pair）

&nbsp;<br>  
### 辅助功能（RF 连接）

```C#
public string GetPipelineState()
```
返回 RF 管道的当前状态

&nbsp;<br>  
```C#
public int GetTotalPackets()
```
返回从当前流式传输会话中收集的数据包总数。