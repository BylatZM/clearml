from clearml import Task
import plotly.graph_objects as go
from PIL import Image
import configparser
import functools 
import inspect 
import os

def clearml_task(project_name, task_name=None, tags=None): 
  def decorator(func):
    @functools.wraps(func) 
    def wrapper(*args, **kwargs): 
      # Автоматическое определение имени задачи 
      automatic_task_name = task_name or func.__name__ 

      # Создание задачи ClearML с указанным названием проекта, названием задачи, а также тегами для задачи (чтобы удобно искать ее) 
      task = Task.init( 
          project_name=project_name,  
          task_name=automatic_task_name, 
          tags=tags or [] 
      )

      # В задаче в раздел "configuration" добавляет раздел "function_signature", где показывает, какие параметры функция принимает и дополнительную информацию по ним
      task.connect_configuration( 
          {k: v for k, v in inspect.signature(func).parameters.items()}, 
          name="function_signature" 
      )

      #Загрузка артефактов (файлов, папок, которые могут понадобиться для обучения модели)
      task.upload_artifact('dancing_human_image', Image.open(os.path.join("./", "dancing.jpg")))
      task.upload_artifact('args_json_file', "./sample.json")
      task.upload_artifact('args_csv_file', "./data.csv")

      # Выполнение основной функции 
      result = func(*args, **kwargs) 

      # Логирование результатов. Имитация результатов на разных ветках цикла. Метод позволяет строить график вкладка "scalars"
      # value - по оси y, iteration - по оси x
      for i in range(len(args)):
        try:
          if i == 0:
            image_open = Image.open(os.path.join("./", "picasso.jpg"))
            task.get_logger().report_image(
              title="Image", 
              series="Picasso", 
              iteration=args[i], 
              image=image_open
            )
            labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
            values = [4500, 2500, 1053, 500]
            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            task.get_logger().report_plotly(
              title="Pie Dio", series="Success", iteration=args[i], figure=fig
            )
            continue
          if i >= round(len(args) / 2):
            raise Exception(f"Ошибка произошла на итерации № {i + 1}")
          task.get_logger().report_scalar( 
              title='Результат',  
              series='Success',  
              value=args[i]*2,
              iteration=args[i]
          )
        except Exception as e:
          task.get_logger().report_scalar( 
            title='Результат',  
            series='Error',  
            value=args[i]*2,
              iteration=args[i]
          )
          # во вкладке console, отдельной строчкой тупо напечатает текст ошибки
          task.get_logger().report_text(str(e))

      # возвращаем результат выполнения функции переданной в декоратор
      return result

    return wrapper 
  return decorator

config = configparser.ConfigParser()
config.read("conf.ini")

@clearml_task(project_name=config.get('args', 'project'), task_name=config.get('args', 'task'), tags=config.get('args', 'tags').split()) 
def process_data(*args, **kwargs): 
  print("This is my args: ", args)
  print("This is my kwargs: ", kwargs)

# Использование декоратора 
result = process_data(1, 2, 3, 4, name="Task", type="Train")