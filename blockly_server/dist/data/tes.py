import yaml

with open('admin_parameters.yaml', encoding=('utf-8')) as file:
    parameters = yaml.load(file, Loader=yaml.FullLoader)
print(parameters)


for key, value in parameters.items():
        if(key == "robot_name"):
            print("Getting robot name: ", value['value'] )
