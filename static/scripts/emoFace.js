import React from "react"


// stateless func component displaying a face image and an emoji
export const EmoFace = (props) => (
    <div className={"emo_face"}>
        <image src={this.props.face} className={"emo_face_profile"}/>
        <span className={"emo_face_emoji"}>{this.props.emoji}</span>
    </div>
)

