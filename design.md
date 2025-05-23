# 文书标注系统
一个用于处理原始文书数据的前后端系统，可对原始文书数据进行过滤，格式化存储，基础信息补全，并交给人工标注，然后靠AI辅助审查，并提交到openai训练平台然后开始训练和验证。

## 大概流程
1. 过滤：平台根据某些条件将所有的输入原始文书数据过滤得到部分原始文书数据。
2. 数据格式化存储：根据文书模板M，将原始文书中的数据填入到模板中得到格式A的文书数据。
3. 基础信息补全（留好接口，暂时空出这部分）：通过调用LLM api，根据构建的prompt进行推理，将推理的数据填入格式A的文书数据中。
4. 任务创建：后台可以通过创建任务，上传需要标注的格式A的文书文件，然后指定需要标注的字段，然后让人工进行标注。人工可以修改对应字段。
5. AI辅助审查（该部分留好接口，暂时空出）：将人工未标注的数据作为输入，构建prompt，让LLM推理来实现人工标注的任务。
6. OPENAI训练数据准备（该部分留好接口，暂时空出）：将人工标注完的数据进行格式转换
7. 模型训练和验证（该部分留好接口，暂时空出）：提交训练任务，并在训练结束之后进行数据验证（将AI标注的结果和人工标注的结果分别与模型微调后进行推理标注的结果进行对比）

## 详细部分

### 基础文书示例
基础文书内容见 wenshu_new2022docId11.jsonl  

格式A的文书数据格式见 example.json

### 创建任务和标注详细流程
1. 创建任务时需要选定标注模板和上传需要标注的文件。如果上传的文件结构和模板不一致则无法通过验证，并给出具体哪里不一致的报错，显示在前端页面上

2. 上传的文书被存放在后端文件夹中，当上传成功和但是却取消创建时，删除已上传成功的文件。并且支持多文件上传。

3. 开始标注时，先获取上传的文件内容，一个页面展现一个json对象在标注界面，以每一个json对象为单位，设置上下切换单位按键，并显示当前是第几个json对象，根据创建任务时的配置规定那些键的值可修改，其余均不可修改。

4. 设置保存按键，当点击保存后，前端会先将数据进行格式校验（按照创建任务时的模板文件），无误后发回后端写入文件中。

### 过滤
1. 根据原始文书数据中的某些字段进行筛选，如 s2,s2代表的是法院单位，可以以此筛选出哪些省份的法院案件。

2. 写出通用筛选接口，具体怎么实现可以让我自己实现。

### 格式化存储
1. 输入是原始文书数据，输出是A。原始文书数据中有些数据可以直接写到A中，有些会扔掉。

2. A中有些数据需要人工或LLM提取，所以只是创建好位置，留给后续处理，先填入默认值，其余部分就是将原始文书数据中的某一部分直接填过来


### 格式验证 
策略是 对json对象进行格式验证，必须符合类似 backend\app\models\task.py中的Document类的结构


### 标注界面的对比
当创建一类对比任务时，可以将由同一份初始数据经过人工标注和LLM推理标注的数据1和2，放入标注页面，二者同时展示在前端页面，然后将差异部分高亮。让人工二次标注。

