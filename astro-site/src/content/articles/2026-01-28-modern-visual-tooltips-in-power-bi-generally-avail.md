---
title: "Modern Visual Tooltips in Power BI (Generally Available)"
title_vi: ""
source: "Power BI Blog"
url: "https://powerbi.microsoft.com/en-us/blog/modern-visual-tooltips-in-power-bi-generally-available/"
topic: "microsoft"
date: "2026-01-28"
excerpt: "Power BI’s latest update introduces an enhancement to how users interact with reports with the general availability of modern visual tooltips. All Power BI reports—from Power BI Desktop to Power BI..."
excerpt_vi: ""
number: 5
publishDate: "2026-01-28T00:00:00Z"
---

Power BI’s latest update introduces an enhancement to how users interact with reports with the general availability of **modern visual tooltips**. All Power BI reports—from Power BI Desktop to Power BI reports in the web, in the mobile app, in Teams, and embedded in any website—now use the updated visual tooltips, making report interactions easier with the built-in actions footer and report creation faster with tooltip styling and colors coming from the report theme.

By default, visual tooltips show the details of the visual’s data point report consumers hover over, such as the name and value. Let’s look at how these updated tooltip features improve both the visual tooltip creation and consumer experiences of Power BI reports.

## 1. Drill actions directly in tooltips

One of the standout features is the **Actions** footer. Users can perform drill down, drill up, and drill through actions directly from the tooltip. This removes the need to right-click or use the visual header. Hovering over a bar in a chart lets you drill down into that data point or drill through to related report pages. This approach streamlines workflows and makes data exploration more intuitive.

![Screenshot of the modern tooltip showing the Actions footer with Drill down and Drill through actions outlined](https://powerbiblogsfd-ep-aveghkfaexa3e4bx.b02.azurefd.net//wp-content/uploads/2026/01/word-image-31994-1.png)

Actions footer of a modern tooltip showing the Drill down and Drill through options.

Report authors can enable or disable the **Actions** footer when editing any report using the Format pane.

![Screenshot of format pane showing Actions group highlighted](https://powerbiblogsfd-ep-aveghkfaexa3e4bx.b02.azurefd.net//wp-content/uploads/2026/01/word-image-31994-2-1.png)

Customize Actions footer in the Format pane.

## 2. Theme-based styling and customization

Modern visual tooltips adopt your report’s theme colors for a consistent and professional look across all visuals. You can customize tooltips further when editing a report, not only by using the **Format pane**, adjusting colors, fonts, and transparency to match your brand or reporting needs, but also when customizing the report theme from the **View** ribbon > **Them****es dropdown** > **Customize current theme** option or importing a custom theme to your report using **Browse for theme.**

![Screenshot of Customize theme dialog with the Tooltip tab selected](https://powerbiblogsfd-ep-aveghkfaexa3e4bx.b02.azurefd.net//wp-content/uploads/2026/01/word-image-31994-3-1.png)

Format tooltip colors within the Customize theme dialog.

Customizing the theme updates tooltips in all existing visuals, not modified individually, and applies to new visuals you create in the report. Modifying the visual individually using the **Format pane** only updates the style for that visual without impacting other visuals or new visuals.

## 3. No impact to existing reports

Previously created reports continue to have the same tooltip experience until the report author edits them to use the new styling and actions footer.

- **New reports:** All tooltips use the modern experience by default, including updated styling from the theme and with the **Actions** footer enabled.
- **Existing reports:** Tooltips remain as they were before this update. To adopt the updated tooltips, select **Reset to default** in the **Format** pane on any visual to update all visuals in the report.

Try out the updated visual tooltips in your Power BI reports today! More interactive and accessible, tooltips help report consumers discover insights faster and with less effort. Custom styling streamlines professional report creation, and the actions footer puts next steps right where users are interacting with the data to take their analysis to the next level.

To learn more, check out the detailed documentation at: [Create Modern Visual Tooltips](https://learn.microsoft.com/power-bi/create-reports/desktop-visual-tooltips?tabs=desktop-new).
