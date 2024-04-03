jiraSample = {
    "fields": {
        "project": {
            "id": "10000"
        },
        "issuetype": {
            "id": "10001"
        },
        "summary": "New Ticket from API",
        "description": {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "description added from postman"
                        }
                    ]
                }
            ]
        },
        "customfield_10033":"1",
        "customfield_10034":"broadband",
        "assignee": {
            "id": "712020:7b50644d-d0eb-4e69-9716-284bc9de20c6"
        },
        "parent": {
            "id": "10000"
        },
        "customfield_10034":"test",
        "reporter": {
            "id": "712020:7b50644d-d0eb-4e69-9716-284bc9de20c6"
        }
    },
    "update": {},
    "watchers": [
        "712020:7b50644d-d0eb-4e69-9716-284bc9de20c6"
    ]
}
freshdeskSample = {
    "description": "Details about the issue...",
    "subject": "Support Needed...",
    "email": "tom@outerspace.com",
    "priority": 1,
    "status": 2,
    "cc_emails": [
        "subhajit.ghosh@airtel.com"
    ]
}

jiraSample['fields']['description']['content'][0]['content'][0]['text'] = "Broadband location change"
