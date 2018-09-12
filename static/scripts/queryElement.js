import React from "react"

import query_data from "./queries"


class QueryElement extends React.Component{
    /*
    props:
    - q_type
    - options
    - submitted
    - handleResponseCallback
    */
    constructor(props){
        super(props)
        this.handleResponse = this.handleResponse.bind(this)
    }
    handleResponse(){
        // this method will only call parent callback when submitted = false
        
    }
    render(){

    }
}

export default QueryElement