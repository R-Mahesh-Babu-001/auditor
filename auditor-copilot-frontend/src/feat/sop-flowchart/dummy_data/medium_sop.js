export const medium_complexity_sop_data = {
        "nodes": [
            {
                "id": "node_start",
                "type": "input",
                "position": {
                    "x": 100,
                    "y": 50
                },
                "data": {
                    "label": "Customer initiates return request"
                },
                "style": {
                    "background": "#e0f7fa",
                    "border": "1px solid #00bcd4",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step2",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 200
                },
                "data": {
                    "label": "Log return request in RMS (Return ID)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionA",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 350
                },
                "data": {
                    "label": "DECISION A: Verify original order exists?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_requestOrder",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 400
                },
                "data": {
                    "label": "Request order # from customer"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_rejectOrderEnd",
                "type": "output",
                "position": {
                    "x": 700,
                    "y": 450
                },
                "data": {
                    "label": "Reject return (cannot provide order) & END"
                },
                "style": {
                    "background": "#ffcdd2",
                    "border": "1px solid #f44336",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step4",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 500
                },
                "data": {
                    "label": "Retrieve order details"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionB",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 650
                },
                "data": {
                    "label": "DECISION B: Return within 30 days?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_managerApproval",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 700
                },
                "data": {
                    "label": "Escalate to Customer Service Manager (Wait 24h)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionB1",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 850
                },
                "data": {
                    "label": "DECISION B1: Manager decision?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_rejectReturn",
                "type": "default",
                "position": {
                    "x": 700,
                    "y": 700
                },
                "data": {
                    "label": "Send rejection notification & Close return"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_endProcess_rejectReturn_S1",
                "type": "output",
                "position": {
                    "x": 700,
                    "y": 850
                },
                "data": {
                    "label": "END PROCESS"
                },
                "style": {
                    "background": "#ffcdd2",
                    "border": "1px solid #f44336",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step6_loopStart",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 950
                },
                "data": {
                    "label": "LOOP START: For Each item in return request"
                },
                "style": {
                    "background": "#e8f5e9",
                    "border": "1px solid #4caf50",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step6_1",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 1100
                },
                "data": {
                    "label": "Verify item eligibility (Mark 'Approved'/'Non-Returnable')"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step6_2",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 1250
                },
                "data": {
                    "label": "Check item condition requirements"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step6_3",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 1400
                },
                "data": {
                    "label": "Calculate refund amount (incl. fees)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionC",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 1550
                },
                "data": {
                    "label": "DECISION C: All items eligible?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_customerConfirmation",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 1600
                },
                "data": {
                    "label": "Contact customer (eligible/non-eligible items), present partial return option (Wait 48h)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionC1",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 1750
                },
                "data": {
                    "label": "DECISION C1: Customer decision?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_cancelReturnEnd",
                "type": "output",
                "position": {
                    "x": 700,
                    "y": 1750
                },
                "data": {
                    "label": "Cancel return request & END"
                },
                "style": {
                    "background": "#ffcdd2",
                    "border": "1px solid #f44336",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_sendReminder",
                "type": "default",
                "position": {
                    "x": 700,
                    "y": 1900
                },
                "data": {
                    "label": "Send reminder (Wait 24h)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_autoCancelEnd",
                "type": "output",
                "position": {
                    "x": 700,
                    "y": 2050
                },
                "data": {
                    "label": "Auto-cancel return & END"
                },
                "style": {
                    "background": "#ffcdd2",
                    "border": "1px solid #f44336",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step9",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 1800
                },
                "data": {
                    "label": "Generate Return Authorization (RA) & shipping label"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step10",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 1950
                },
                "data": {
                    "label": "Send return instructions & shipping label to customer"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step11",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 2100
                },
                "data": {
                    "label": "Update return status to 'Awaiting Item Return'"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step12",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 2250
                },
                "data": {
                    "label": "WAIT for returned items to arrive at warehouse (up to 14 days)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionD",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 2400
                },
                "data": {
                    "label": "DECISION D: Items received within 14 days?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_followUp",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 2450
                },
                "data": {
                    "label": "Follow-up: Contact customer (Wait 7 additional days)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionD1",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 2600
                },
                "data": {
                    "label": "DECISION D1: Follow-up result?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_closeNoShipEnd",
                "type": "output",
                "position": {
                    "x": 700,
                    "y": 2550
                },
                "data": {
                    "label": "Close request (customer confirms not shipping) & END"
                },
                "style": {
                    "background": "#ffcdd2",
                    "border": "1px solid #f44336",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_closeNoResponseEnd",
                "type": "output",
                "position": {
                    "x": 700,
                    "y": 2700
                },
                "data": {
                    "label": "Close request (no response) & END"
                },
                "style": {
                    "background": "#ffcdd2",
                    "border": "1px solid #f44336",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step14",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 2700
                },
                "data": {
                    "label": "Scan RA number & log item receipt in RMS"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step15_loopStart",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 2850
                },
                "data": {
                    "label": "LOOP START: For Each returned item"
                },
                "style": {
                    "background": "#e8f5e9",
                    "border": "1px solid #4caf50",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step15_1",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 3000
                },
                "data": {
                    "label": "Verify item matches original order"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_wrongItemHandling",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 3050
                },
                "data": {
                    "label": "Wrong Item Handling (Document, Contact Customer)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionD2",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 3200
                },
                "data": {
                    "label": "DECISION D2: Customer made error?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step15_2",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 3300
                },
                "data": {
                    "label": "Inspect item condition"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionE",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 3450
                },
                "data": {
                    "label": "DECISION E: Item in resalable condition?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_damagedItemAssessment",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 3500
                },
                "data": {
                    "label": "Document damage with photos"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionE1",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 3650
                },
                "data": {
                    "label": "DECISION E1: Damage type?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_customerDamageHandling",
                "type": "default",
                "position": {
                    "x": 700,
                    "y": 3700
                },
                "data": {
                    "label": "Apply damage fee, contact customer (Wait for ack.)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_escalateDamage",
                "type": "default",
                "position": {
                    "x": 700,
                    "y": 3850
                },
                "data": {
                    "label": "Escalate customer damage dispute to manager"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step15_4",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 3900
                },
                "data": {
                    "label": "Verify accessories & packaging (Deduct if missing)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step16",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 4050
                },
                "data": {
                    "label": "Calculate final refund amount"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionF",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 4200
                },
                "data": {
                    "label": "DECISION F: Determine refund method (Original payment)"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_ccRefund",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 4250
                },
                "data": {
                    "label": "Process Credit Card Refund"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionF1",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 4400
                },
                "data": {
                    "label": "DECISION F1: Credit Card Refund successful?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_alternateRefund",
                "type": "default",
                "position": {
                    "x": 700,
                    "y": 4450
                },
                "data": {
                    "label": "Contact customer for alternate refund method"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_bankRefund",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 4600
                },
                "data": {
                    "label": "Request bank account details, Process Bank Transfer"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_accountCredit",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 4750
                },
                "data": {
                    "label": "Apply credit to customer account"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_checkRefund",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 4900
                },
                "data": {
                    "label": "Generate & Mail Check Refund"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step18",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 5050
                },
                "data": {
                    "label": "Update return status to 'Refund Processed'"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step19",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 5200
                },
                "data": {
                    "label": "Send refund confirmation email"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step20_loopStart",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 5350
                },
                "data": {
                    "label": "LOOP START: For Each accepted returned item"
                },
                "style": {
                    "background": "#e8f5e9",
                    "border": "1px solid #4caf50",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionG",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 5500
                },
                "data": {
                    "label": "DECISION G: Determine item disposition?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_dispositionPerfect",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 5450
                },
                "data": {
                    "label": "Return to regular inventory (IF perfect condition)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1"
                }
            },
            {
                "id": "node_dispositionOpenBox",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 5600
                },
                "data": {
                    "label": "Move to 'Open Box' inventory (IF good, opened)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_dispositionRefurb",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 5750
                },
                "data": {
                    "label": "Send to refurbishment (IF damaged but repairable)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_dispositionDisposal",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 5900
                },
                "data": {
                    "label": "Send to disposal/recycling (IF not salvageable)"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step20_2",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 6050
                },
                "data": {
                    "label": "Update inventory records"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step21",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 6200
                },
                "data": {
                    "label": "Generate return summary report"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step22",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 6350
                },
                "data": {
                    "label": "Update customer profile with return history"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_step23",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 6500
                },
                "data": {
                    "label": "Close return request in RMS (status 'Completed')"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_decisionH",
                "type": "default",
                "position": {
                    "x": 100,
                    "y": 6650
                },
                "data": {
                    "label": "DECISION H: 3rd+ return in 90 days?"
                },
                "style": {
                    "background": "#ffecb3",
                    "border": "1px solid #ffc107",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_flagAccount",
                "type": "default",
                "position": {
                    "x": 400,
                    "y": 6700
                },
                "data": {
                    "label": "Flag account for fraud prevention review"
                },
                "style": {
                    "background": "#fff",
                    "border": "1px solid #ddd",
                    "borderRadius": "8px"
                }
            },
            {
                "id": "node_endProcessFinal",
                "type": "output",
                "position": {
                    "x": 100,
                    "y": 6800
                },
                "data": {
                    "label": "END PROCESS"
                },
                "style": {
                    "background": "#ffcdd2",
                    "border": "1px solid #f44336",
                    "borderRadius": "8px"
                }
            }
        ],
        "edges": [
            {
                "id": "edge_start_to_step2",
                "source": "node_start",
                "target": "node_step2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step2_to_decisionA",
                "source": "node_step2",
                "target": "node_decisionA",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionA_orderFound_to_step4",
                "source": "node_decisionA",
                "target": "node_step4",
                "type": "smoothstep",
                "animated": false,
                "label": "IF order found"
            },
            {
                "id": "edge_decisionA_orderNotFound_to_requestOrder",
                "source": "node_decisionA",
                "target": "node_requestOrder",
                "type": "smoothstep",
                "animated": false,
                "label": "IF order not found"
            },
            {
                "id": "edge_requestOrder_valid_to_step4",
                "source": "node_requestOrder",
                "target": "node_step4",
                "type": "smoothstep",
                "animated": false,
                "label": "IF valid order provided"
            },
            {
                "id": "edge_requestOrder_invalid_to_rejectOrderEnd",
                "source": "node_requestOrder",
                "target": "node_rejectOrderEnd",
                "type": "smoothstep",
                "animated": false,
                "label": "IF cannot provide"
            },
            {
                "id": "edge_step4_to_decisionB",
                "source": "node_step4",
                "target": "node_decisionB",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionB_within30_to_step6",
                "source": "node_decisionB",
                "target": "node_step6_loopStart",
                "type": "smoothstep",
                "animated": false,
                "label": "IF within 30 days"
            },
            {
                "id": "edge_decisionB_30to60_to_managerApproval",
                "source": "node_decisionB",
                "target": "node_managerApproval",
                "type": "smoothstep",
                "animated": false,
                "label": "IF 30-60 days"
            },
            {
                "id": "edge_decisionB_beyond60_to_rejectReturn",
                "source": "node_decisionB",
                "target": "node_rejectReturn",
                "type": "smoothstep",
                "animated": false,
                "label": "IF beyond 60 days"
            },
            {
                "id": "edge_managerApproval_to_decisionB1",
                "source": "node_managerApproval",
                "target": "node_decisionB1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionB1_approved_to_step6",
                "source": "node_decisionB1",
                "target": "node_step6_loopStart",
                "type": "smoothstep",
                "animated": false,
                "label": "IF approved"
            },
            {
                "id": "edge_decisionB1_rejected_to_rejectReturn",
                "source": "node_decisionB1",
                "target": "node_rejectReturn",
                "type": "smoothstep",
                "animated": false,
                "label": "IF rejected"
            },
            {
                "id": "edge_rejectReturn_to_endProcess_S1",
                "source": "node_rejectReturn",
                "target": "node_endProcess_rejectReturn_S1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step6_loopStart_to_step6_1",
                "source": "node_step6_loopStart",
                "target": "node_step6_1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step6_1_to_step6_2",
                "source": "node_step6_1",
                "target": "node_step6_2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step6_2_to_step6_3",
                "source": "node_step6_2",
                "target": "node_step6_3",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step6_3_to_decisionC",
                "source": "node_step6_3",
                "target": "node_decisionC",
                "type": "smoothstep",
                "animated": false,
                "label": "After all items processed"
            },
            {
                "id": "edge_decisionC_allEligible_to_step9",
                "source": "node_decisionC",
                "target": "node_step9",
                "type": "smoothstep",
                "animated": false,
                "label": "IF all items eligible"
            },
            {
                "id": "edge_decisionC_someNonEligible_to_customerConfirmation",
                "source": "node_decisionC",
                "target": "node_customerConfirmation",
                "type": "smoothstep",
                "animated": false,
                "label": "IF some non-returnable"
            },
            {
                "id": "edge_customerConfirmation_to_decisionC1",
                "source": "node_customerConfirmation",
                "target": "node_decisionC1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionC1_accepts_to_step9",
                "source": "node_decisionC1",
                "target": "node_step9",
                "type": "smoothstep",
                "animated": false,
                "label": "IF customer accepts"
            },
            {
                "id": "edge_decisionC1_rejects_to_cancelReturnEnd",
                "source": "node_decisionC1",
                "target": "node_cancelReturnEnd",
                "type": "smoothstep",
                "animated": false,
                "label": "IF customer rejects"
            },
            {
                "id": "edge_decisionC1_noResponse_to_sendReminder",
                "source": "node_decisionC1",
                "target": "node_sendReminder",
                "type": "smoothstep",
                "animated": false,
                "label": "IF no response (48h)"
            },
            {
                "id": "edge_sendReminder_to_autoCancelEnd",
                "source": "node_sendReminder",
                "target": "node_autoCancelEnd",
                "type": "smoothstep",
                "animated": false,
                "label": "IF still no response (24h)"
            },
            {
                "id": "edge_step9_to_step10",
                "source": "node_step9",
                "target": "node_step10",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step10_to_step11",
                "source": "node_step10",
                "target": "node_step11",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step11_to_step12",
                "source": "node_step11",
                "target": "node_step12",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step12_to_decisionD",
                "source": "node_step12",
                "target": "node_decisionD",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionD_received_to_step14",
                "source": "node_decisionD",
                "target": "node_step14",
                "type": "smoothstep",
                "animated": false,
                "label": "IF items received"
            },
            {
                "id": "edge_decisionD_notReceived_to_followUp",
                "source": "node_decisionD",
                "target": "node_followUp",
                "type": "smoothstep",
                "animated": false,
                "label": "IF no items received"
            },
            {
                "id": "edge_followUp_to_decisionD1",
                "source": "node_followUp",
                "target": "node_decisionD1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionD1_itemsArrive_to_step14",
                "source": "node_decisionD1",
                "target": "node_step14",
                "type": "smoothstep",
                "animated": false,
                "label": "IF items arrive"
            },
            {
                "id": "edge_decisionD1_customerNotShipping_to_closeNoShipEnd",
                "source": "node_decisionD1",
                "target": "node_closeNoShipEnd",
                "type": "smoothstep",
                "animated": false,
                "label": "IF customer not shipping"
            },
            {
                "id": "edge_decisionD1_noResponse_to_closeNoResponseEnd",
                "source": "node_decisionD1",
                "target": "node_closeNoResponseEnd",
                "type": "smoothstep",
                "animated": false,
                "label": "IF no response"
            },
            {
                "id": "edge_step14_to_step15_loopStart",
                "source": "node_step14",
                "target": "node_step15_loopStart",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step15_loopStart_to_step15_1",
                "source": "node_step15_loopStart",
                "target": "node_step15_1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step15_1_match_to_step15_2",
                "source": "node_step15_1",
                "target": "node_step15_2",
                "type": "smoothstep",
                "animated": false,
                "label": "IF match confirmed"
            },
            {
                "id": "edge_step15_1_wrongItem_to_wrongItemHandling",
                "source": "node_step15_1",
                "target": "node_wrongItemHandling",
                "type": "smoothstep",
                "animated": false,
                "label": "IF wrong item"
            },
            {
                "id": "edge_wrongItemHandling_to_decisionD2",
                "source": "node_wrongItemHandling",
                "target": "node_decisionD2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionD2_customerError_to_step12",
                "source": "node_decisionD2",
                "target": "node_step12",
                "type": "smoothstep",
                "animated": false,
                "label": "IF customer error (Return to re-receipt)"
            },
            {
                "id": "edge_decisionD2_warehouseError_to_step15_2",
                "source": "node_decisionD2",
                "target": "node_step15_2",
                "type": "smoothstep",
                "animated": false,
                "label": "IF warehouse error"
            },
            {
                "id": "edge_step15_2_to_decisionE",
                "source": "node_step15_2",
                "target": "node_decisionE",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionE_resalable_to_step15_4",
                "source": "node_decisionE",
                "target": "node_step15_4",
                "type": "smoothstep",
                "animated": false,
                "label": "IF resalable"
            },
            {
                "id": "edge_decisionE_damaged_to_damagedItemAssessment",
                "source": "node_decisionE",
                "target": "node_damagedItemAssessment",
                "type": "smoothstep",
                "animated": false,
                "label": "IF damaged/used"
            },
            {
                "id": "edge_damagedItemAssessment_to_decisionE1",
                "source": "node_damagedItemAssessment",
                "target": "node_decisionE1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionE1_shippingDamage_to_step15_4",
                "source": "node_decisionE1",
                "target": "node_step15_4",
                "type": "smoothstep",
                "animated": false,
                "label": "IF shipping damage"
            },
            {
                "id": "edge_decisionE1_customerUse_to_customerDamageHandling",
                "source": "node_decisionE1",
                "target": "node_customerDamageHandling",
                "type": "smoothstep",
                "animated": false,
                "label": "IF customer use damage"
            },
            {
                "id": "edge_customerDamageHandling_to_escalateDamage",
                "source": "node_customerDamageHandling",
                "target": "node_escalateDamage",
                "type": "smoothstep",
                "animated": false,
                "label": "IF customer disputes"
            },
            {
                "id": "edge_customerDamageHandling_resolved_to_step15_4",
                "source": "node_customerDamageHandling",
                "target": "node_step15_4",
                "type": "smoothstep",
                "animated": false,
                "label": "IF resolved (Acknowledged)"
            },
            {
                "id": "edge_escalateDamage_to_step15_4",
                "source": "node_escalateDamage",
                "target": "node_step15_4",
                "type": "smoothstep",
                "animated": false,
                "label": "IF manager approves"
            },
            {
                "id": "edge_step15_4_to_step16",
                "source": "node_step15_4",
                "target": "node_step16",
                "type": "smoothstep",
                "animated": false,
                "label": "After all items processed"
            },
            {
                "id": "edge_step16_to_decisionF",
                "source": "node_step16",
                "target": "node_decisionF",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionF_cc_to_ccRefund",
                "source": "node_decisionF",
                "target": "node_ccRefund",
                "type": "smoothstep",
                "animated": false,
                "label": "IF credit card"
            },
            {
                "id": "edge_decisionF_bank_to_bankRefund",
                "source": "node_decisionF",
                "target": "node_bankRefund",
                "type": "smoothstep",
                "animated": false,
                "label": "IF bank transfer"
            },
            {
                "id": "edge_decisionF_account_to_accountCredit",
                "source": "node_decisionF",
                "target": "node_accountCredit",
                "type": "smoothstep",
                "animated": false,
                "label": "IF on account"
            },
            {
                "id": "edge_decisionF_cash_to_checkRefund",
                "source": "node_decisionF",
                "target": "node_checkRefund",
                "type": "smoothstep",
                "animated": false,
                "label": "IF cash"
            },
            {
                "id": "edge_ccRefund_to_decisionF1",
                "source": "node_ccRefund",
                "target": "node_decisionF1",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionF1_successful_to_step18",
                "source": "node_decisionF1",
                "target": "node_step18",
                "type": "smoothstep",
                "animated": false,
                "label": "IF successful"
            },
            {
                "id": "edge_decisionF1_failed_to_alternateRefund",
                "source": "node_decisionF1",
                "target": "node_alternateRefund",
                "type": "smoothstep",
                "animated": false,
                "label": "IF failed"
            },
            {
                "id": "edge_alternateRefund_to_decisionF",
                "source": "node_alternateRefund",
                "target": "node_decisionF",
                "type": "smoothstep",
                "animated": false,
                "label": "RETURN to Step 17"
            },
            {
                "id": "edge_bankRefund_to_step18",
                "source": "node_bankRefund",
                "target": "node_step18",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_accountCredit_to_step18",
                "source": "node_accountCredit",
                "target": "node_step18",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_checkRefund_to_step18",
                "source": "node_checkRefund",
                "target": "node_step18",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step18_to_step19",
                "source": "node_step18",
                "target": "node_step19",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step19_to_step20_loopStart",
                "source": "node_step19",
                "target": "node_step20_loopStart",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step20_loopStart_to_decisionG",
                "source": "node_step20_loopStart",
                "target": "node_decisionG",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionG_perfect_to_dispositionPerfect",
                "source": "node_decisionG",
                "target": "node_dispositionPerfect",
                "type": "smoothstep",
                "animated": false,
                "label": "IF perfect condition"
            },
            {
                "id": "edge_decisionG_openBox_to_dispositionOpenBox",
                "source": "node_decisionG",
                "target": "node_dispositionOpenBox",
                "type": "smoothstep",
                "animated": false,
                "label": "IF good, opened"
            },
            {
                "id": "edge_decisionG_repairable_to_dispositionRefurb",
                "source": "node_decisionG",
                "target": "node_dispositionRefurb",
                "type": "smoothstep",
                "animated": false,
                "label": "IF damaged, repairable"
            },
            {
                "id": "edge_decisionG_notSalvageable_to_dispositionDisposal",
                "source": "node_decisionG",
                "target": "node_dispositionDisposal",
                "type": "smoothstep",
                "animated": false,
                "label": "IF not salvageable"
            },
            {
                "id": "edge_dispositionPerfect_to_step20_2",
                "source": "node_dispositionPerfect",
                "target": "node_step20_2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_dispositionOpenBox_to_step20_2",
                "source": "node_dispositionOpenBox",
                "target": "node_step20_2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_dispositionRefurb_to_step20_2",
                "source": "node_dispositionRefurb",
                "target": "node_step20_2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_dispositionDisposal_to_step20_2",
                "source": "node_dispositionDisposal",
                "target": "node_step20_2",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step20_2_to_step21",
                "source": "node_step20_2",
                "target": "node_step21",
                "type": "smoothstep",
                "animated": false,
                "label": "After all items processed"
            },
            {
                "id": "edge_step21_to_step22",
                "source": "node_step21",
                "target": "node_step22",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step22_to_step23",
                "source": "node_step22",
                "target": "node_step23",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_step23_to_decisionH",
                "source": "node_step23",
                "target": "node_decisionH",
                "type": "smoothstep",
                "animated": false
            },
            {
                "id": "edge_decisionH_flag_to_flagAccount",
                "source": "node_decisionH",
                "target": "node_flagAccount",
                "type": "smoothstep",
                "animated": false,
                "label": "IF 3rd+ return in 90 days"
            },
            {
                "id": "edge_decisionH_noFlag_to_endProcessFinal",
                "source": "node_decisionH",
                "target": "node_endProcessFinal",
                "type": "smoothstep",
                "animated": false,
                "label": "ELSE"
            },
            {
                "id": "edge_flagAccount_to_endProcessFinal",
                "source": "node_flagAccount",
                "target": "node_endProcessFinal",
                "type": "smoothstep",
                "animated": false
            }
        ]
    }