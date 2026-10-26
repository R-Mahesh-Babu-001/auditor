export const low_complexity_sop_data = {
        "nodes": [
            {
                "id": "node_1",
                "type": "input",
                "position": {
                    "x": 200,
                    "y": 50
                },
                "data": {
                    "label": "Step 1: Employee submits time-off request"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_2",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 150
                },
                "data": {
                    "label": "Step 2: System logs request with timestamp and ID"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_3",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 250
                },
                "data": {
                    "label": "Step 3: System sends notification to manager"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_A",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 350
                },
                "data": {
                    "label": "Step 4: DECISION A - Is request for sick leave?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_5",
                "type": "default",
                "position": {
                    "x": 0,
                    "y": 470
                },
                "data": {
                    "label": "Step 5: Manager receives immediate notification"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_B",
                "type": "default",
                "position": {
                    "x": 0,
                    "y": 570
                },
                "data": {
                    "label": "Step 6: DECISION B - Check sick leave duration?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_6_1_auto_approve",
                "type": "default",
                "position": {
                    "x": -200,
                    "y": 670
                },
                "data": {
                    "label": "Step 6: Auto-approve (1-3 days sick leave)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_6_2_require_doc",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 670
                },
                "data": {
                    "label": "Step 6: Require medical documentation (wait 48h)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_B_doc",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 770
                },
                "data": {
                    "label": "DECISION: Doc received within 48h?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_6_2_doc_approve",
                "type": "default",
                "position": {
                    "x": 0,
                    "y": 870
                },
                "data": {
                    "label": "Step 6: Approve (medical doc received)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_7_send_reminder",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 870
                },
                "data": {
                    "label": "Step 7: Send reminder for medical doc (wait 24h)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_B_rem_doc",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 970
                },
                "data": {
                    "label": "DECISION: Doc received within 24h (reminder)?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_7_doc_approve",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 1070
                },
                "data": {
                    "label": "Step 7: Approve (doc received after reminder)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_13_reject_sick",
                "type": "default",
                "position": {
                    "x": 600,
                    "y": 1070
                },
                "data": {
                    "label": "Step 7: Reject request (no medical doc)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_8",
                "type": "default",
                "position": {
                    "x": 600,
                    "y": 470
                },
                "data": {
                    "label": "Step 8: Manager reviews time-off request"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_C",
                "type": "default",
                "position": {
                    "x": 600,
                    "y": 570
                },
                "data": {
                    "label": "Step 9: DECISION C - Check team coverage?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_D",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 670
                },
                "data": {
                    "label": "Step 10: DECISION D - Check employee leave balance?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_10_approve_std",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 770
                },
                "data": {
                    "label": "Step 10: Approve (sufficient balance available)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_11_insufficient",
                "type": "default",
                "position": {
                    "x": 600,
                    "y": 770
                },
                "data": {
                    "label": "Step 11: Notify insufficient balance; offer options (wait 48h)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_E",
                "type": "default",
                "position": {
                    "x": 600,
                    "y": 870
                },
                "data": {
                    "label": "Step 11: DECISION E - Employee choice?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_11_modify_return",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 970
                },
                "data": {
                    "label": "Step 11: Employee modifies request (RETURN to Step 8)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_11_unpaid_approve",
                "type": "default",
                "position": {
                    "x": 600,
                    "y": 970
                },
                "data": {
                    "label": "Step 11: Approve (employee accepts unpaid leave)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_11_cancel",
                "type": "default",
                "position": {
                    "x": 800,
                    "y": 970
                },
                "data": {
                    "label": "Step 11: Employee cancels request"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_11_no_resp_cancel",
                "type": "default",
                "position": {
                    "x": 1000,
                    "y": 970
                },
                "data": {
                    "label": "Step 11: Auto-cancel (no response)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_12_conditional",
                "type": "default",
                "position": {
                    "x": 800,
                    "y": 670
                },
                "data": {
                    "label": "Step 12: Manager contacts for alternative dates (wait 48h)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_F",
                "type": "default",
                "position": {
                    "x": 800,
                    "y": 770
                },
                "data": {
                    "label": "Step 12: DECISION F - Employee response?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_12_alt_return",
                "type": "default",
                "position": {
                    "x": 600,
                    "y": 870
                },
                "data": {
                    "label": "Step 12: Employee provides alternative dates (RETURN to Step 8)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_12_insist_original",
                "type": "default",
                "position": {
                    "x": 900,
                    "y": 870
                },
                "data": {
                    "label": "Step 12: Employee insists on original dates"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_F_manager",
                "type": "default",
                "position": {
                    "x": 900,
                    "y": 970
                },
                "data": {
                    "label": "DECISION: Manager approves despite coverage?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_12_manager_approve",
                "type": "default",
                "position": {
                    "x": 800,
                    "y": 1070
                },
                "data": {
                    "label": "Step 12: Manager approves despite coverage issue"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_12_manager_reject",
                "type": "default",
                "position": {
                    "x": 1000,
                    "y": 1070
                },
                "data": {
                    "label": "Step 12: Manager rejects original dates"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_12_no_resp_reject",
                "type": "default",
                "position": {
                    "x": 1100,
                    "y": 870
                },
                "data": {
                    "label": "Step 12: Auto-reject (no response)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_13_final_reject",
                "type": "output",
                "position": {
                    "x": 900,
                    "y": 1220
                },
                "data": {
                    "label": "Step 13: REJECTED - Update status, notify, log"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_14",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 1220
                },
                "data": {
                    "label": "Step 14: APPROVED - Update request status"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_15",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 1320
                },
                "data": {
                    "label": "Step 15: Send approval confirmation to employee"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_16",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 1420
                },
                "data": {
                    "label": "Step 16: Update employee leave balance"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_G",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 1520
                },
                "data": {
                    "label": "Step 17: DECISION G - Time-off starts within 7 days?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_17_send_reminder_pre_leave",
                "type": "default",
                "position": {
                    "x": 0,
                    "y": 1620
                },
                "data": {
                    "label": "Step 17: Send reminder to employee & manager"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_18_add_to_calendar",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 1720
                },
                "data": {
                    "label": "Step 18: Add approved time-off to team calendar"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_dec_H",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 1820
                },
                "data": {
                    "label": "Step 19: DECISION H - Backup coverage needed?"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_19_notify_backup",
                "type": "default",
                "position": {
                    "x": 0,
                    "y": 1920
                },
                "data": {
                    "label": "Step 19: Send notification to designated backup person"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_20",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 2020
                },
                "data": {
                    "label": "Step 20: Generate time-off confirmation document"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_21",
                "type": "default",
                "position": {
                    "x": 200,
                    "y": 2120
                },
                "data": {
                    "label": "Step 21: Close time-off request with status 'Completed'"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            },
            {
                "id": "node_22_end",
                "type": "output",
                "position": {
                    "x": 200,
                    "y": 2220
                },
                "data": {
                    "label": "Step 22: END PROCESS"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "minWidth": "180px"
                }
            }
        ],
        "edges": [
            {
                "id": "e1-2",
                "source": "node_1",
                "target": "node_2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e2-3",
                "source": "node_2",
                "target": "node_3",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e3-dec_A",
                "source": "node_3",
                "target": "node_dec_A",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decA-5",
                "source": "node_dec_A",
                "target": "node_5",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decA-8",
                "source": "node_dec_A",
                "target": "node_8",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e5-decB",
                "source": "node_5",
                "target": "node_dec_B",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decB-6_1",
                "source": "node_dec_B",
                "target": "node_6_1_auto_approve",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decB-6_2",
                "source": "node_dec_B",
                "target": "node_6_2_require_doc",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e6_2-decB_doc",
                "source": "node_6_2_require_doc",
                "target": "node_dec_B_doc",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decB_doc-6_2_approve",
                "source": "node_dec_B_doc",
                "target": "node_6_2_doc_approve",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decB_doc-7_reminder",
                "source": "node_dec_B_doc",
                "target": "node_7_send_reminder",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e7_reminder-decB_rem_doc",
                "source": "node_7_send_reminder",
                "target": "node_dec_B_rem_doc",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decB_rem_doc-7_approve",
                "source": "node_dec_B_rem_doc",
                "target": "node_7_doc_approve",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decB_rem_doc-13_reject_sick",
                "source": "node_dec_B_rem_doc",
                "target": "node_13_reject_sick",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e8-decC",
                "source": "node_8",
                "target": "node_dec_C",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decC-decD",
                "source": "node_dec_C",
                "target": "node_dec_D",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decC-12_conditional",
                "source": "node_dec_C",
                "target": "node_12_conditional",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decD-10_approve_std",
                "source": "node_dec_D",
                "target": "node_10_approve_std",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decD-11_insufficient",
                "source": "node_dec_D",
                "target": "node_11_insufficient",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e11_insufficient-decE",
                "source": "node_11_insufficient",
                "target": "node_dec_E",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decE-11_modify_return",
                "source": "node_dec_E",
                "target": "node_11_modify_return",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e11_modify_return-8",
                "source": "node_11_modify_return",
                "target": "node_8",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decE-11_unpaid_approve",
                "source": "node_dec_E",
                "target": "node_11_unpaid_approve",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decE-11_cancel",
                "source": "node_dec_E",
                "target": "node_11_cancel",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decE-11_no_resp_cancel",
                "source": "node_dec_E",
                "target": "node_11_no_resp_cancel",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e12_conditional-decF",
                "source": "node_12_conditional",
                "target": "node_dec_F",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decF-12_alt_return",
                "source": "node_dec_F",
                "target": "node_12_alt_return",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e12_alt_return-8",
                "source": "node_12_alt_return",
                "target": "node_8",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decF-12_insist_original",
                "source": "node_dec_F",
                "target": "node_12_insist_original",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e12_insist_original-decF_manager",
                "source": "node_12_insist_original",
                "target": "node_dec_F_manager",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decF_manager-12_manager_approve",
                "source": "node_dec_F_manager",
                "target": "node_12_manager_approve",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decF_manager-12_manager_reject",
                "source": "node_dec_F_manager",
                "target": "node_12_manager_reject",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decF-12_no_resp_reject",
                "source": "node_dec_F",
                "target": "node_12_no_resp_reject",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e6_1_approve-14",
                "source": "node_6_1_auto_approve",
                "target": "node_14",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e6_2_approve-14",
                "source": "node_6_2_doc_approve",
                "target": "node_14",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e7_approve-14",
                "source": "node_7_doc_approve",
                "target": "node_14",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e10_approve_std-14",
                "source": "node_10_approve_std",
                "target": "node_14",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e11_unpaid_approve-14",
                "source": "node_11_unpaid_approve",
                "target": "node_14",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e12_manager_approve-14",
                "source": "node_12_manager_approve",
                "target": "node_14",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e13_reject_sick-13_final",
                "source": "node_13_reject_sick",
                "target": "node_13_final_reject",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e11_cancel-13_final",
                "source": "node_11_cancel",
                "target": "node_13_final_reject",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e11_no_resp_cancel-13_final",
                "source": "node_11_no_resp_cancel",
                "target": "node_13_final_reject",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e12_manager_reject-13_final",
                "source": "node_12_manager_reject",
                "target": "node_13_final_reject",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e12_no_resp_reject-13_final",
                "source": "node_12_no_resp_reject",
                "target": "node_13_final_reject",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e14-15",
                "source": "node_14",
                "target": "node_15",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e15-16",
                "source": "node_15",
                "target": "node_16",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e16-decG",
                "source": "node_16",
                "target": "node_dec_G",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decG-17_reminder",
                "source": "node_dec_G",
                "target": "node_17_send_reminder_pre_leave",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e17_reminder-18",
                "source": "node_17_send_reminder_pre_leave",
                "target": "node_18_add_to_calendar",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decG-18",
                "source": "node_dec_G",
                "target": "node_18_add_to_calendar",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e18-decH",
                "source": "node_18_add_to_calendar",
                "target": "node_dec_H",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decH-19_notify",
                "source": "node_dec_H",
                "target": "node_19_notify_backup",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e19_notify-20",
                "source": "node_19_notify_backup",
                "target": "node_20",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e_decH-20",
                "source": "node_dec_H",
                "target": "node_20",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e20-21",
                "source": "node_20",
                "target": "node_21",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "e21-22_end",
                "source": "node_21",
                "target": "node_22_end",
                "type": "smoothstep",
                "animated": false
            }
        ]
    }