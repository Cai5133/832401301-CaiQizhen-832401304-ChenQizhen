# 界面参考与使用范围

## 当前明亮版参考

[Horizon UI](https://github.com/horizon-ui/horizon-ui-chakra)，MIT 许可证。阅读 `src/theme/styles.js` 的浅色底与紫色品牌色，以及 `src/views/admin/default/index.jsx` 的统计卡片排列方式。借鉴浅色工作台、独立圆角卡片、柔和层次和品牌色强调；没有引入 React、Chakra、图表、账户、付费功能或商业模板。

结合用户提供的界面参考图，将紫、青、奶油金配成轻柔的浅色卡片。顶部新增本项目 SVG 电话本形象，含头像标签页、笑脸、邮件与电话元素；形象在不同屏幕尺寸下保持清晰。资料列表、右侧详情以及现有业务流程仍为原 Vue 工程。许可证保存在 `licenses/horizon-ui.txt`。

## 早期深色版参考

[satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin)，MIT 许可证。查看了项目 README 界面图、用户列表页面 `src/features/users/index.tsx`、顶栏 `src/components/layout/header.tsx` 和 `src/styles/theme.css`。

借鉴范围：固定侧栏与顶栏的工作台布局、紧凑的标题操作区、深色背景层级、细边框、列表行和按钮的层级关系。没有引入其 React 页面、路由、登录、收入图表、角色权限或测试数据。

通讯录继续使用当前 Vue 工程。增加适合联系人信息的右侧详情区；主色调整为蓝色，侧栏使用本项目成员与通讯录入口，图表区域不适用于本作业，未采用。

## 图标

使用 [Lucide Vue](https://lucide.dev/guide/vue) 的官方 `@lucide/vue` 图标包统一工具栏、导航和联系方式类型图标。许可声明位于 `licenses/lucide.txt`。

## 英文版调整

统一英文界面与姓名缩写头像；深色底调整为接近黑色的中性色，采用蓝色选中状态、细分隔线和更清晰的标题层级。删除侧栏底部课程项目标识，保留团队成员及真实功能入口。未增加无实际功能的装饰控件。

## 作业内容

仅调整视觉呈现。收藏、多条联系方式、Excel 导入导出、接口字段、Excel 格式、分工、仓库和博客要求继续按作业执行。当前修改保留在本地，待审阅后再决定是否上传。
