import {MdNotifications , MdNotificationsActive} from "react-icons/md"
import React from "react"


class ButtonWithAlert extends React.Component{
    /*
    props:
        - alert_active bool
    */
    render(){
        if(this.props.alert_active === true) {
            return(<MdNotifications/>)
        } else {
            return(<MdNotificationsActive/>)
        }
    }
}

export default ButtonWithAlert