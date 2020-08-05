# 定义函数，获取GoodsCategory模型类的一级分类，二级分类，三级分类的类名

def get_breadcrumb(category):  # 这里的category传入是一个对象
    # 定义一个字典，作为返回的值
    dict = {}
    # 判断Category是哪一级

    # 是否为第一级
    if category.parent is None:
        dict['cat1'] = category.name
    # 是否为第二级
    elif category.parent.parent is None:
        dict['cat2'] = category.name
        dict['cat1'] = category.parent.name
    # 是否为第三级
    elif category.parent.parent.parent is None:
        dict['cat3'] = category.name
        dict['cat2'] = category.parent.name
        dict['cat1'] = category.parent.parent.name

    return dict