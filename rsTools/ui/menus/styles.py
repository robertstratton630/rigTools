__style__ = '''QMenu{
                            font-size: 11px;
                            font-family: "Lucida Grande",Arial,Tahoma;
                            background-color: #333;
                            margin: 0;
                            border: 2px solid rgba (32,32,32,160);
                        }
                            
                QMenu::item,QLabel{     
                                    padding:5px 18px 4px 24px;
                                    color:#CCC;
                                  }
                                   
                QMenu::item:disabled{
                                        color:#888;
                                    }
                                    
                QMenu::item:selected,QLabel:hover,QLabel:selected{
                                                                    background-color:#555;
                                                                    color:#EEE;
                                                                  }
                QMenu::item:separator{
                                        height:1px;
                                        background:#444;
                                        margin:2px 0px 2px 0px;
                                     }
                                     
                QMenu::QCheckBox{
                                    background-color:#222;
                                }
                '''
