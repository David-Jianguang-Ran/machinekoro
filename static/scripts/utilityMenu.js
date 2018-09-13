import { MdMenu, MdBugReport, MdExitToApp, } from "react-icons/md"
import React from "react"


import ExpandableButton from "./expandableButton"
import KickPlayerMenu from "./kickPlayerMenu"

class UtilityMenu extends ExpandableButton{
    /*
    props:
        - ws_manager
        - match_state
        - is_prime

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
        this.expanded = (
            <div className={"utility_menu"}>
                    <div className={"utility_button"}>
                        <MdExitToApp onClick={window.close()}/>
                    </div>
                    <div className={"utility_button"}>
                        <MdBugReport onClick={window.close()}/>
                    </div>
                    <KickPlayerMenu ws_manager={this.props.ws_manager}
                                    game_state={this.props.game_state}
                                    is_prime={this.props.is_prime}
                    />
            </div>
        )
    }
}

export default UtilityMenu