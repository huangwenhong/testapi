from datetime import datetime, timedelta
import hashlib
import random
import requests  # pyright: ignore[reportMissingModuleSource]
import sys
import uuid
sys.stdout.reconfigure(encoding="utf-8")
from urllib.parse import urlparse, parse_qs
from typing import Optional, List, Dict, Any, Tuple

from get_res import GetRes
url1 = "https://grouptest.cpsol.net/djgroupon/outerUser/usernameLogin.do"
url2 = "https://grouptest.cpsol.net/djgroupon/outerUser/getUserInfo.do"
url3="https://grouptest.cpsol.net/djgroupon/address/loadUserAddress.do"

url4= "https://grouptest.cpsol.net/djgroupon/address/setUserBrowseAddress.do"
url5= "https://grouptest.cpsol.net/djgroupon/address/getUserBrowseAddress.do"
url6= "https://grouptest.cpsol.net/djgroupon/product/loadGrouponList.do"
url7= "https://grouptest.cpsol.net/djgroupon/product/loadGoodDetails.do"
url8= "https://grouptest.cpsol.net/djgroupon/address/loadUserAddress.do"
url9= "https://grouptest.cpsol.net/djgroupon/placeOrder/check.do"
url10= "https://grouptest.cpsol.net/djgroupon/newPlaceOrder/editParams.do"
# 拿到金额和面积还有积分的接口
url10a="https://grouptest.cpsol.net/djgroupon/newPlaceOrder/newPricingProtocol.do"
# 拿到交期
url10b="https://grouptest.cpsol.net/djgroupon/product/getIntervalOfDeliveryTime.do"

# 拿到积分策略
url10c="https://grouptest.cpsol.net/djgroupon/grouponpay/getGrouponPayOrder.do"
payload10c={"forderId":"MGRN202512191557774858","forderarea":"3301"}


url11= "https://grouptest.cpsol.net/djgroupon/order/newSaveOrder.do"
url12= "https://grouptest.cpsol.net/djgroupon/grouponpay/paymentOfBlance.do"

base_headers = {
    "Content-Type": "application/json",
    "device": "web",
    "version": "v6.1.20",
}

# 账号相关配置（可在这里自定义修改）
ACCOUNT_CONFIG = {
    # 登录账号（用户名 / 手机号）
    "username": "15355094538",
    # 登录密码的 MD5 值（不是明文）
    "password_md5": "339b522501ca880a03acbd86943b1129",
    # 支付密码明文（用于本地计算 MD5）
    "pay_password_plain": "121212",
}




def login_and_get_token(
    login_username: Optional[str] = None,
    login_password_md5: Optional[str] = None,
    pay_password_plain: Optional[str] = None,
    fmateriallength: str = "100",
    fmaterialwidth: str = "200",
    famount: str = "100"
) -> Tuple[requests.Session, str]:
    """
    登录并获取 token，动态构建所有接口参数
    
    参数:
        fmateriallength: 材料长度（毫米），默认100
        fmaterialwidth: 材料宽度（毫米），默认200
        famount: 数量，默认100
        login_username: 登录账号（不传则使用 ACCOUNT_CONFIG 里的 username）
        login_password_md5: 登录密码 MD5（不传则使用 ACCOUNT_CONFIG 里的 password_md5）
        pay_password_plain: 支付密码明文（不传则使用 ACCOUNT_CONFIG 里的 pay_password_plain）
        fmateriallength: 材料长度（毫米），默认100
        fmaterialwidth: 材料宽度（毫米），默认200
        famount: 数量，默认100
    
    返回: (session, token)
    """
    s = requests.Session()
    
    # 1) 登录：根据传入参数或 ACCOUNT_CONFIG 动态构造登录入参
    username = login_username or ACCOUNT_CONFIG["username"]
    password_md5 = login_password_md5 or ACCOUNT_CONFIG["password_md5"]

    payload1 = {
        "username": username,
        "password": password_md5,
        "loginType": "WEB",
    }

    resp1 = s.post(url1, headers=base_headers, json=payload1, timeout=60)
    GetRes._print_req_resp("weblogin", resp1)
    data1 = resp1.json()
    if not data1.get("success") or data1.get("code") != 100000:
        raise Exception(f"登录失败: {data1}")
 
    # 2) 获取用户信息
    payload2 = {}
    resp2 = s.post(url2, headers=base_headers, json=payload2, timeout=60)
    data2 = resp2.json()
    if not data2.get("success") or data2.get("code") != 100000:
        raise Exception(f"获取用户信息失败: {data2}")
  
    # 从用户信息中提取关键字段
    user_data = data2.get("data", {})
    user_id = user_data.get("fid") or user_data.get("userId") or user_data.get("id")
    fkeyarea = user_data.get("fkeyarea") or "3301"  # 默认值
    
    # 3) 加载用户地址列表
    payload3 = {"fkeyarea": str(fkeyarea)}
    resp3 = s.post(url3, headers=base_headers, json=payload3, timeout=60)
    data3 = resp3.json()
    if not data3.get("success") or data3.get("code") != 100000:
        raise Exception(f"加载地址失败: {data3}")
    
    # 从地址列表中获取默认地址或第一个地址
    address_list = data3.get("data", [])
    if not address_list:
        raise Exception("没有可用地址")
    
    default_address = next((addr for addr in address_list if addr.get("fdefault") == 1), address_list[0])
    fprovince = default_address.get("fprovincename")
    fcity = default_address.get("fcityname")
    fcounty = default_address.get("fareaname")
    fstreet = default_address.get("ftownname")
    fuserbrowseareacode = default_address.get("fcodetown") or default_address.get("fcodearea")
    address_id = default_address.get("fid")
    
    
    # 4) 设置用户浏览地址
    payload4 = {
        "fprovince": fprovince,
        "fcity": fcity,
        "fcounty": fcounty,
        "fstreet": fstreet,
        "fuserbrowseareacode": fuserbrowseareacode,
        "fuserid": user_id
    }
    resp4 = s.post(url4, headers=base_headers, json=payload4, timeout=60)
    data4 = resp4.json()
    if not data4.get("success"):
        print(f"设置浏览地址警告: {data4}")

    # 5) 获取用户浏览地址
    payload5 = {}
    resp5 = s.post(url5, headers=base_headers, json=payload5, timeout=60)
    data5 = resp5.json()
    if data5.get("success") and data5.get("code") == 100000:
        browse_data = data5.get("data")
        # 处理data可能是list或dict的情况
        if isinstance(browse_data, list) and len(browse_data) > 0:
            # 如果是列表，取第一个元素
            browse_data = browse_data[0]
            fuserBrowseAreaCode = browse_data.get("fuserbrowseareacode") or fuserbrowseareacode
        elif isinstance(browse_data, dict):
            # 如果是字典，直接获取
            fuserBrowseAreaCode = browse_data.get("fuserbrowseareacode") or fuserbrowseareacode
        else:
            fuserBrowseAreaCode = fuserbrowseareacode
    else:
        fuserBrowseAreaCode = fuserbrowseareacode

    # 6) 加载团购商品列表
    payload6 = {
        "fflutetype": 0,
        "fgrouptype": 0,
        "fkeyarea": int(fkeyarea) if isinstance(fkeyarea, str) else fkeyarea,
        "fproductname": "",  # 可以留空或从前端传入
        "fgroupareaid": int(fkeyarea) if isinstance(fkeyarea, str) else fkeyarea,
        "systemplatform": 3,
        "limitbuildnumber": 1,
        "fsupplierid": "",
        "fuserBrowseAreaCode": int(fuserBrowseAreaCode) if isinstance(fuserBrowseAreaCode, str) else fuserBrowseAreaCode
    }
    resp6 = s.post(url6, headers=base_headers, json=payload6, timeout=60)
    data6 = resp6.json()
    
    if not data6.get("success") or data6.get("code") != 100000:
        raise Exception(f"加载商品列表失败: {data6}")
    
    # 从商品列表中随机选择一个可购买的商品
    data6_data = data6.get("data", {})
    # 处理data可能是list或dict的情况
    if isinstance(data6_data, list):
        product_list = data6_data
    elif isinstance(data6_data, dict):
        product_list = data6_data.get("list", [])
    else:
        product_list = []
    
    if not product_list:
        raise Exception("商品列表为空")
    
    # 优先过滤可购买商品（如果返回里带有 fpurchaseState 字段）
    purchasable_products = [
        p for p in product_list
        if p.get("fpurchaseState") in (True, "true", "Y", "y", 1)
    ] or product_list

    selected_product = random.choice(purchasable_products)
    product_fid = selected_product.get("fid")
    product_name = selected_product.get("fproductname", "")

    # 7) 加载商品详情
    payload7 = {
        "fid": product_fid,
        "fuserBrowseAreaCode": str(fuserBrowseAreaCode)
    }
    resp7 = s.post(url7, headers=base_headers, json=payload7, timeout=60)
    data7 = resp7.json()
  
    
    if not data7.get("success") or data7.get("code") != 100000:
        raise Exception(f"加载商品详情失败: {data7}")
    
    product_detail = data7.get("data", {})
    # 提取商品详情中的关键字段
    product_fid = product_detail.get("fid")
    fmaterialid = product_detail.get("fmaterialid")
    fflutetype = product_detail.get("fflutetype")
    flayer = product_detail.get("flayer")
    fmateriallengthplus = product_detail.get("fmateriallengthplus")
    fmaterialwidthplus = product_detail.get("fmaterialwidthplus")
    fkeyarea_product = product_detail.get("fkeyarea")
    # 注意：接口返回字段为 fgroupareaid（全小写），没有 fgroupAreaId
    # 所以这里先从 fgroupareaid 取值，再赋给我们后续要用的 fgroupAreaId 变量
    fgroupareaid = product_detail.get("fgroupareaid")
    salesType = product_detail.get("salesType", 
    "platform_group")
    pricingPlanGenre = product_detail.get("pricingPlanGenre", 0)
    cardboardGenre = product_detail.get("cardboardGenre")
    fmarketingplanid = product_detail.get("fmarketingplanid")
    fmktplanchangeid = product_detail.get("fmktplanchangeid")
    fgroupAreaId = fgroupareaid
    fsupplierid = product_detail.get("fsupplierid")
    flogistics = product_detail.get("flogistics")
    funitprice = product_detail.get("fPrice") or product_detail.get("funitprice")
    fpaymentsl1 = product_detail.get("fpaymentsl1")
    fintegral = product_detail.get("fintegral")
    fmaxorderlength = product_detail.get("fmaxorderlength")
    fminorderlength = product_detail.get("fminorderlength")
    fmaxorderwidth = product_detail.get("fmaxorderwidth")
    fminorderwidth = product_detail.get("fminorderwidth")
    fminarea = product_detail.get("fminarea")
    fnormalarea = product_detail.get("fnormalarea")
    
    # 8) 再次加载用户地址（用于订单）
    payload8 = {"fkeyarea": str(fkeyarea)}
    resp8 = s.post(url8, headers=base_headers, json=payload8, timeout=60)
    data8 = resp8.json()
 
    
    if not data8.get("success") or data8.get("code") != 100000:
        raise Exception(f"加载地址失败: {data8}")
    
    # 获取默认地址ID用于下单
    address_list_order = data8.get("data", [])
    default_address_order = next((addr for addr in address_list_order if addr.get("fdefault") == 1), address_list_order[0])
    faddressId = default_address_order.get("fid")
    
    # 9) 检查订单
    # 需要先构建检查数据，这里使用商品详情中的信息
    payload9 = {
        "chekDataList": [{
            "fid": product_fid,
            "changeid": fmktplanchangeid,  # 从商品详情获取
            "fkeyarea": str(fkeyarea_product),
            "fmaterialfid": fmaterialid,
            "fflutetype": fflutetype,
            "flayer": flayer,
            "fmateriallengthplus": fmateriallengthplus,
            "fmaterialwidthplus": fmaterialwidthplus,
            "fuserBrowseAreaCode": int(fuserBrowseAreaCode) if isinstance(fuserBrowseAreaCode, str) else fuserBrowseAreaCode,
            "schemeId": None,
            "pricingPlanGenre": pricingPlanGenre,
            "cardboardGenre": cardboardGenre,
            "changeNumber": None,
            "salesType": salesType
        }],
        "systemplatform": 3,
        "limitbuildnumber": 1
    }
    resp9 = s.post(url9, headers=base_headers, json=payload9, timeout=60)
    data9 = resp9.json()

    
    if not data9.get("success"):
        # 如果检查失败，尝试从响应中获取新的changeid
        if data9.get("code") == 800005:  # 营销方案发生变更
            print("营销方案发生变更，需要重新获取changeid")
            # 重新获取商品详情以获取最新的changeid
            resp7_retry = s.post(url7, headers=base_headers, json=payload7, timeout=60)
            data7_retry = resp7_retry.json()
            if data7_retry.get("success"):
                product_detail = data7_retry.get("data", {})
                fmktplanchangeid = product_detail.get("fmktplanchangeid")
                # 更新payload9并重试
                payload9["chekDataList"][0]["changeid"] = fmktplanchangeid
                resp9 = s.post(url9, headers=base_headers, json=payload9, timeout=60)
                data9 = resp9.json()
                print(f"重试检查订单: {data9}")
    
    # 从检查结果中获取changeid（如果返回了新的）
    check_data = data9.get("data")
    if isinstance(check_data, dict) and check_data.get("changeid"):
        fmktplanchangeid = check_data.get("changeid")
    
    # 10) 编辑参数
    payload10 = {
        "fid": product_fid,
        "fuserBrowseAreaCode": str(fuserBrowseAreaCode),
        "fboxModel": 0,  # 默认值，可以从商品详情获取
        "fstaveType": "3",  # 默认值
        "fseries": 1,  # 默认值
        "flayer": flayer,
        "pricingPlanGenre": pricingPlanGenre,
        "cardboardGenre": cardboardGenre,
        "fflutetype": fflutetype,
        "salesType": salesType
    }
    resp10 = s.post(url10, headers=base_headers, json=payload10, timeout=60)
    data10 = resp10.json()

    
    if not data10.get("success"):
        raise Exception(f"编辑参数失败: {data10}")
    
    # 从编辑参数结果中获取实际使用的值
    edit_data = data10.get("data", {})
    fboxModel = edit_data.get("fboxModel", {}).get("defaultValue", 0)
    fstaveType = edit_data.get("fstaveType", {}).get("defaultValue", "3")
    fseries = edit_data.get("fseries", {}).get("defaultValue", 1)

    # 10a) 调用新定价接口，获取「金额 / 面积 / 积分」等精确值
    payload10a = {
        "clientType": 2,
        "fuserId": user_id,
        "fid": product_fid,
        "fboxModel": fboxModel,
        "fboxLength": None,
        "fboxWidth": None,
        "fboxHeight": None,
        "fstaveType": fstaveType,
        "fseries": str(fseries),
        "fhline": "",
        "fvline": "",
        "famount": famount,
        "fhformula": 0,
        "fvformula": 0,
        "fuserBrowseAreaCode": int(fuserBrowseAreaCode) if isinstance(fuserBrowseAreaCode, str) else fuserBrowseAreaCode,
        "purchaseType": 1,
        "changePrice": 2,
        "fmaterialLength": fmateriallength,
        "fmaterialWidth": fmaterialwidth,
        "optimalGateWidth": None,
        "cutNumber": "",
        "openingNumber": None,
        "optionalLarghezza": False,
        "salesType": salesType,
    }
    resp10a = s.post(url10a, headers=base_headers, json=payload10a, timeout=60)
    data10a = resp10a.json()
 
    print(data10a)
    if not data10a.get("success"):
        raise Exception(f"定价接口失败: {data10a}")

    price_data = data10a.get("data", {}) or {}
    # 单价（每平米价格），接口字段 priceCalculation / groupPurchasePrice
    funitprice_str = str(
        price_data.get("priceCalculation")
        or price_data.get("groupPurchasePrice")
        or funitprice
        or "0"
    )
    # 总价、面积、积分等全部从接口返回里取
    famountprice = str(price_data.get("ftotalPrice") or "0")
    fproductarea = str(price_data.get("ftotalArea") or "0")
    fgiveintegral = str(price_data.get("integral") or "0")
    
    payload10b = {"productId":product_fid}
    
    resp10b = s.post(url10b, headers=base_headers, json=payload10b, timeout=60)
    data10b = resp10b.json()
    deliveryTime = data10b.get("data", {}) or {}
    fdeliveryTime = str(deliveryTime.get("maxDeliveryTime") or "0")













   

















    payload11 = {
        "faddressId": faddressId,
        "childOrder": [{
            "fgroupgoodid": product_fid,
            "flogistics": flogistics,
            "fgroupgoodname": product_name,
            "funitprice": funitprice_str,
            "famountprice": famountprice,
            "flayer": flayer,
            "fmanufacturer": fsupplierid,
            "fmateriafid": fmaterialid,
            "fboxmodel": fboxModel,
            "fboxlength": None,
            "fboxwidth": None,
            "fboxheight": None,
            "fmateriallength": fmateriallength,
            "fmaterialwidth": fmaterialwidth,
            "fmaterialname": fmaterialid,
            "fstavetype": fstaveType,
            "fseries": str(fseries),
            "fhline": "",
            "fvline": "",
            "fhlineformula": None,
            "fvlineformula": None,
            "famount": famount,
            "famountpiece": int(float(famount)),
            "fhformula": 0,
            "fvformula": 0,
            "fgiveintegral": fgiveintegral,
            "fproductarea": fproductarea,
            "fmarktingplanid": fmktplanchangeid,
            "fmktplanchangeid": fmktplanchangeid,
            "fordertype": 1,
            "fintegral": fintegral,
            "fmaxorderlength": fmaxorderlength,
            "fminorderlength": fminorderlength,
            "fmaxorderwidth": fmaxorderwidth,
            "fminorderwidth": fminorderwidth,
            "fmateriallengthplus": fmateriallengthplus,
            "fmaterialwidthplus": fmaterialwidthplus,
            "fsmallprice": None,
            "fminarea": fminarea,
            "fnormalarea": fnormalarea,
            "fflutetype": fflutetype,
            "fpaymentsl1": fpaymentsl1,
            "fkeyarea": str(fkeyarea_product),
            "fgroupAreaId": fgroupAreaId,
            "pricingPlanGenre": pricingPlanGenre,
            "changeNumber": None,
            "cardboardGenre": cardboardGenre,
            "schemeId": None,
            "productionParameters": None,
            "optimalGateWidth": 0,
            "openingNumber": None,
            "cutNumber": "",
            "fuserBrowseAreaCode": int(fuserBrowseAreaCode) if isinstance(fuserBrowseAreaCode, str) else fuserBrowseAreaCode,
            "purchaseType": 1,
            "activityPlanId": None,
            "fdeliveryTime": fdeliveryTime,
            "ferporderid": "",
            "materialActivityId": None,
            "salesType": salesType
        }],
        "fgoodnumber": 1,
        "ftotalPrice": famountprice,
        "area": fgroupAreaId,
        "fclient": 1,
        "uuid": str(uuid.uuid4()),
        "client": "web",
        "fuseCouponTotalPrice": famountprice,
        "fuseCouponTotalCredits": int(float(fgiveintegral)),
        "fuserBrowseAreaCode": int(fuserBrowseAreaCode) if isinstance(fuserBrowseAreaCode, str) else fuserBrowseAreaCode,
        "fintegralToUseTotal": 0,
        "integralUseType": 1,
        "couponUseType": 1,
        "payType": ""
    }
    
    resp11 = s.post(url11, headers=base_headers, json=payload11, timeout=60)
    print(payload11)
    data11 = resp11.json()

 
    if not data11.get("success"):
        print(f"保存订单失败: {data11}")
        # 如果失败是因为价格变动，可以重新获取商品详情并重试
        if data11.get("code") == "000101017":  # 价格变动
            print("商品价格发生变动，需要重新获取价格信息")
    else:
        # 12) 支付（如果订单创建成功）
        order_data = data11.get("data", {})
        # 接口返回里字段是 forderid（全小写），这里做兼容处理
        forderId = order_data.get("forderId") or order_data.get("forderid")
        if forderId:
            # 这里需要支付密码，优先使用函数入参，其次使用 ACCOUNT_CONFIG
            # 使用 MD5 对支付密码进行加密
            pay_plain = pay_password_plain or ACCOUNT_CONFIG["pay_password_plain"]
            pay_md5 = hashlib.md5(pay_plain.encode("utf-8")).hexdigest()

            payload12 = {
                "forderId": forderId,
                "forderarea": str(fkeyarea),
                "fkeyarea": str(fkeyarea),
                "fpaytype": 0,
                "famount": int(float(famountprice) * 100),  # 转换为分
                "userId": user_id,
                 "fpaypassword": pay_md5,  # 使用 MD5 加密后的支付密码
                "fisUseIntegral": "",
                "partnerRateModelList": [{
                    "acceptName": "供应商默认费率",
                    "acceptRate": "0.00",
                    "fmanufacturer": None,
                    "facceptancepayler": 1
                }]
            }
            resp12 = s.post(url12, headers=base_headers, json=payload12, timeout=60)
            data12 = resp12.json()
            print(f"支付结果: {data12}")
            pass
    return s
login_and_get_token()