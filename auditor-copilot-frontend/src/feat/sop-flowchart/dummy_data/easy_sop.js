export const easy_complexity_sop_data = {
        "nodes": [
            {
                "id": "n1",
                "type": "input",
                "position": {
                    "x": 100,
                    "y": 100
                },
                "data": {
                    "label": "Receive new employee request from HR"
                },
                "style": {
                    "background": "#f0f9ff",
                    "border": "1px solid #007bff",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "n2",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 300
                },
                "data": {
                    "label": "Send welcome email to the employee"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "n3",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 500
                },
                "data": {
                    "label": "Assign workstation and login credentials"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "n4",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 700
                },
                "data": {
                    "label": "Provide initial training and orientation"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "n5",
                "type": "output",
                "position": {
                    "x": 100,
                    "y": 900
                },
                "data": {
                    "label": "Confirm completion with HR and manager"
                },
                "style": {
                    "background": "#f9fff0",
                    "border": "1px solid #28a745",
                    "borderRadius": "8px"
                }
            }
        ],
        "edges": [
            {
                "id": "e1-2",
                "source": "n1",
                "target": "n2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e2-3",
                "source": "n2",
                "target": "n3",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e3-4",
                "source": "n3",
                "target": "n4",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e4-5",
                "source": "n4",
                "target": "n5",
                "type": "smoothstep",
                "animated": false
            }
        ]
    }


