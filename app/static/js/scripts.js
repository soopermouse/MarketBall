function loadPowerBIReport() {
    var reportContainer = document.getElementById('powerbi-report');
    var reportId = "YOUR_POWERBI_REPORT_ID";
    var embedUrl = "https://app.powerbi.com/reportEmbed?reportId=" + reportId;
    var token = "YOUR_POWERBI_EMBED_TOKEN";

    var config = {
        type: 'report',
        tokenType: models.TokenType.Embed,
        accessToken: token,
        embedUrl: embedUrl,
        id: reportId,
        permissions: models.Permissions.All,
        settings: {
            panes: { filters: { visible: false } }
        }
    };

    powerbi.embed(reportContainer, config);
}