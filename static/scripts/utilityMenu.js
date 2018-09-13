import { MdMenu, MdBugReport, MdExitToApp, MdPanTool } from "react-icons/md"
import React from "react"


import ExpandableButton from "./expandableButton"
import KickPlayerMenu from "./kickPlayerMenu"

class UtilityButton extends ExpandableButton{
    /*
    props:
        - ws_manager
        - match_state

    children:
        <for prime player>
        - kick player menu
        <everyone>
        - concede & quit
        - report bug (no text)
    */
    constructor(props){
        super(props)
        this.button =(<MdMenu/>)
        this.expanded = this.prepareMenu()
    }
    reportBug(){

    }
    prepareMenu(){
        if (this.props.ws_manager.context.is_prime === true){
            return(
                <div className={"utility_menu"}>
                    <div className={"utility_button"}>
                        <MdExitToApp onClick={}/>
                    </div>
                    <div className={"utility_button"}>
                        <MdBugReport onClick={this.reportBug}/>
                    </div>
                    <KickPlayerMenu ws_manager={this.props.ws_manager}
                                    game_state={this.props.game_state}
                    />
                </div>
            )
        } else {

        }
    }


}