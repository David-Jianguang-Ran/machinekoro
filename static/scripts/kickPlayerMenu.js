import { MdPanTool } from "react-icons/md"
import React from "react"


import ExpandableButton from "./expandableButton"
import LobbyPlayerList from "./lobbyPlayerList"

class KickPlayerMenu extends ExpandableButton{
    /*
    props:
    - ws_manager
    - match_state
    - is_prime

    */
    constructor(props){
        super(props)
        this.button = (<MdPanTool className={"utility_button"}/>)
        this.expanded = (
            <LobbyPlayerList ws_manager={this.props.ws_manager}
                             match_state={this.props.match_state}
                             is_prime={this.props.is_prime}
            />
        )
    }
}

export default KickPlayerMenu