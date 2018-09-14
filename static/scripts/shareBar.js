import React from "react"

class ShareBar extends React.Component{
    /*
    This component renders a join game link text for players to share
    */
    render(){
        // sorry for the hard coded url....  NoteK@ieg
        let url ="http://127.0.0.1:8000/machinekoro/join"
        url.concat(this.props.match_id)
        return(
            <div id={"share_bar"}>
                <label>
                    Share the following link to invite friends to a game!
                    <a>url</a>
                </label>
            </div>
        )
    }
}

export default ShareBar