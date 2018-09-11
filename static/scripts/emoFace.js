import React from "react"

class EmoFace extends React.Component{
    render(){
        if (this.props.selected === true){
            return(
                <div className={"emo_face_selected"}>
                    <image src={this.props.face} className={"emo_face_profile"}/>
                    <span className={"emo_face_emoji"}>{this.props.emoji}</span>
                </div>
            )
        } else {
            return (
                <div className={"emo_face"}>
                    <image src={this.props.face} className={"emo_face_profile"}/>
                    <span className={"emo_face_emoji"}>{this.props.emoji}</span>
                </div>
            )
        }
    }
}

export default EmoFace

