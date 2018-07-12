import React from 'react'
import HelpOverlay from './helpOverlay'
import Menu from "./menu";


// this is the parent component for
// - Nav/Menu
//      - back concede and back to home
//      - about me
//      - see source code on github
// - Help Overlay
// common for all views

class commonComponent extends React.Component{
    render(){
        return(
            <div id={'common_bar'}>
                <HelpOverlay/>
                <Menu/>
            </div>
            )

    }
}

export default commonComponent
