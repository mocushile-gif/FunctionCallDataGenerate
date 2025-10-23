GET_TOOL_DEFINE_FROM_TOOLACE = """请提取出以下str中所有的函数定义，并用json格式表达,你需要按这样的格式：
   {"name": "newAddress", "description": "Generates a new Ethereum address that can be used to send or receive funds. Do not lose the password! We can't restore access to an address if you lose it.", "parameters": {"type": "dict", "properties": {"password": {"description": "The password for the new Ethereum address", "type": "string"}}, "required": ["password"]}, "required": null}
   需要提取的str:
   """

DOMAIN_LIST = ["Science", "Entertainment", "Commerce", "Data", "Communication", "Artificial Intelligence", "Art",
               "Engineering", "Health", "Economics", "Environment", "Education", "Gaming", "Devices", "Politics",
               "Travel", "Psychology", "History", "Cybersecurity", "Lifestyle", "Logistics", "Events", "Automation",
               "Food", "Construction", "Energy", "Animal Welfare", "Medical", "Nutrition", "Others"]

DOMAIN_LIST_STR = "[Science,Entertainment,Commerce,Data,Communication,Artificial Intelligence,Art,Engineering,Health,Economics,Environment,Education,Gaming,Devices,Politics,Travel,Psychology,History,Cybersecurity,Lifestyle,Logistics,Events,Automation,Food,Construction,Energy,Animal Welfare,Medical,Nutrition,Others]"


SORT_SAMPLE_DOMAIN = """你是一个资深的API设计师，我将给你提供一个API的相关定义，你的任务是对这个API可能应用的领域进行分类，以下是API的定义：
###API定义：
{api_tool_define}

###需要进行分类的种类,如果都不属于以下具体的分类，则归于others：
"""+DOMAIN_LIST_STR+"""

经过思考后对API进行分类，以下是你的回复必须要遵循的json格式:
"""


SORT_SAMPLE_DOMAIN_RESPONSE_FORMAT = str({"thought":"你对于API的理解，以及你的分类依据","sort":"你对API的分类结果"})

#固定使用20个Example
COARSE_INITIAL_GENERATE = """你是一个对于现实世界有很深理解的API设计师，我将给你提供一些{domain} Domains下API的相关定义，你的任务是根据以下这些API定义分析它实际的使用范围，进一步对Domains进行粗粒度的划分.
例如：
将Entertainment Domains进一步细分为:["Music","Book","Cinema","Film","Activity Event","Recreation","Dance","Media","Anime","YouTube","Podcast","Festival","Board Games","Video","Stand-up Comedy","Sports","Theater","Others"]

###API定义:
{EXAMPLE_1}
{EXAMPLE_2}
{EXAMPLE_3}
{EXAMPLE_4}
{EXAMPLE_5}
{EXAMPLE_6}
{EXAMPLE_7}
{EXAMPLE_8}
{EXAMPLE_9}
{EXAMPLE_10}
{EXAMPLE_11}
{EXAMPLE_12}
{EXAMPLE_13}
{EXAMPLE_14}
{EXAMPLE_15}
{EXAMPLE_16}
{EXAMPLE_17}
{EXAMPLE_18}
{EXAMPLE_19}
{EXAMPLE_20}

###请经过思考后对{domain} Domains进行进一步粗粒度分类，要求分类尽可能细致详细并且符合实际生活的场景，请以以下JSON格式回复:
"""

COARSE_INITIAL_GENERATE_RESPONSE_FORMAT = """{"thought": "对于API和Domains的理解，以及分类依据", "category":[{"category_1":"Explanation of the scope covered by this category."},{"category_2":"Explanation of the scope covered by this category."},...]}"""

COARSE_COMPLETE_GENERATE = """你是一个对于现实世界有很深理解的API设计师，我将给你提供一些{domain} Domains下API的相关定义以及对于{domain} Domains的一些粗粒度分类，你的任务是对现有的粗粒度分类进行新增与修正，达到粗粒度分类对{domain} Domain的划分更合理与具有通用性.

###现有{domain} Domains的粗粒度分类:{coarse_basic_domain}

###API定义:
{EXAMPLE_1}
{EXAMPLE_2}
{EXAMPLE_3}
{EXAMPLE_4}
{EXAMPLE_5}
{EXAMPLE_6}
{EXAMPLE_7}
{EXAMPLE_8}
{EXAMPLE_9}
{EXAMPLE_10}
{EXAMPLE_11}
{EXAMPLE_12}
{EXAMPLE_13}
{EXAMPLE_14}
{EXAMPLE_15}
{EXAMPLE_16}
{EXAMPLE_17}
{EXAMPLE_18}
{EXAMPLE_19}
{EXAMPLE_20}
{EXAMPLE_20}
{EXAMPLE_21}
{EXAMPLE_22}
{EXAMPLE_23}
{EXAMPLE_24}
{EXAMPLE_25}
{EXAMPLE_26}
{EXAMPLE_27}
{EXAMPLE_28}
{EXAMPLE_29}
{EXAMPLE_30}

###请经过思考后判断{domain} Domains现有分类是否完善，请以以下JSON格式回复:
"""

COARSE_COMPLETE_GENERATE_RESPONSE_FORMAT = """
# 如果现有分类结果足够完善，则回复:
# {"thought":"对于API和现有分类的理解","classification perfect":"yes"}
# 如果现有分类结果不够完善，则对现有分类进行新增和整理,请注意新增分类时尽可能考虑分类的通用性与粗粒度,返回你修改后的分类标准:
# {"thought":"对于API和现有分类的理解","classification perfect":"no","revised category":[{"revised_category_1":"Explanation of the scope covered by this new category."},{"revised_category_2":"Explanation of the scope covered by this category."},...]}
# """


SORT_SAMPLE_COARSE_DOMAIN = """
你是一个资深的API设计师，我将给你提供一个{domain} Domains下API的相关定义，你的任务是对API可能应用的子领域进行分类，以下是API的定义：
###API定义：
{api_tool_define}

###需要进行分类的种类,如果都不属于以下具体的分类，则归于Others：
{sub_domain_dict}

经过思考后对API进行分类，以下是你的回复必须要遵循的json格式:
"""

FINE_GENERATE_PROMPT = """
你是一个对于现实世界有很深理解的API设计师，我将给你提供一些主领域为{domain} Domains，粗粒度分类领域为{coarse_domain}的API相关定义，其主要包括的范围为{coarse_domain_define}
###你的任务是对现有的粗粒度分类进行进一步细粒度分类，要求细粒度分类后尽量分类清晰，同时全面覆盖{coarse_domain}粗粒度分类领域.

###目前你可以参考{coarse_domain}的进一步细粒度分类结果：{tiny_basic_domain}
###以下是主领域为{domain} Domains，粗粒度分类为{coarse_domain}的一些API定义：
"""


FINE_GENERATE_PROMPT_RESPONSE_FORMAT = """
# 如果现有分类结果足够完善，则回复:
# {"thought":"对于API和现有分类的理解","classification perfect":"yes"}
# 如果现有分类结果不够完善，则对现有分类进行新增和整理,请注意分类时尽可能考虑分类的通用性与全面性,按照以下JSON格式回复:
# {"thought":"对于API和现有分类的理解","classification perfect":"no","revised category":[{"revised_category_1":"Explanation of the scope covered by this new category."},{"revised_category_2":"Explanation of the scope covered by this category."},...]}"""


GENERATE_FUNCTIONS_PROMPT = """你是一个资深的功能设计师，我将给你提供一个具有层级关系的具体领域，你需要设计该领域下应该有哪些具体功能项可以帮忙实现用户的不同需求。
--Domain：{domain_name}
    |--Coarse Domain:{coarse_domain_name}:{coarse_domain_define}
        |--Tiny Domain:{tiny_domain_name}:{tiny_domain_define}"""


GENERATE_FUNCTIONS_PROMPT_RESPONSE_FORMAT = """

###请按照以下JSON格式回复:
{"thought":"对于该具体领域的理解以及可能具有的功能项的思考","function":["function_1":{"define":"Definition of Functionalities","example":["Specific example of function items"]},...]}
"""

if __name__ == '__main__':
    print(SORT_SAMPLE_COARSE_DOMAIN)
