## 关于app_id app_key app_secret
### 对于平台来说, 需要给你的 你的开发者账号分配对应的权限
* app_id
    是用来标记你的开发者账号的, 是你的用户id, 这个id 在数据库添加检索, 方便快速查找
* app_key
    和 app_secret是一对出现的账号, 同一个 app_id 可以对应多个 app_key+app_secret, 这样 平台就可以分配你不一样的权限, 比如 app_key1 + app_secect1 只有只读权限 但是 app_key2+app_secret2 有读写权限.. 这样你就可以把对应的权限 放给不同的开发者.  其中权限的配置都是直接跟app_key 做关联的, app_key 也需要添加数据库检索, 方便快速查找
* 至于为什么要有app_key + app_secret 这种成对出现的机制呢
    因为要加密通常在首次验证(类似登录场景) ,你需要用 app_key(标记要申请的权限有哪些) + app_secret(密码, 表示你真的拥有这个权限) 来申请一个token, 就是我们经常用到的 access_token, 之后的数据请求, 就直接提供access_token 就可以验证权限了.  
### 顺便再说一下简化的场景
* 省去 app_id
    他默认每一个用户有且仅有一套权限配置, 所以直接将 app_id = app_key , 然后外加一个app_secret就够了. 
* 省去app_id和 app_key
    相当于 app_id = app_key = app_secret,  通常用于开放性接口的地方, 特别是很多地图类api 都采用这种模式, 这种模式下, 带上app_id 的目的仅仅是统计 某一个用户调用接口的次数而已了.
