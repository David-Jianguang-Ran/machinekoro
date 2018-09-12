import React from "./react"

import ButtonWithAlert from "./buttonWithAlert"
import QueryElement from "./queryElement"

class QueryResponder extends React.Component{
    /*
    This component presents messages with key "action.query" to the user via a QueryElement Component

    state:
        - quert_set
        - response_set
    props:
        - ws_manager


    children:
        [- QueryElement (dynamic)]
    */
    constructor(props){
        super(props)
        this.state = {
            "expanded": false,
            "query_set":null,
            "response_set":null
        }
        this.handleIncomingQuerySet = this.handleIncomingQuerySet.bind(this)
        this.handleResponseCallback = this.handleResponseCallback.bind(this)
        this.sendResponseToServer = this.sendResponseToServer.bind(this)
    }
    componentDidMount(){
        // register message listener with ws_manager
        this.props.ws_manager.addMessageListener("action.query",this.handleIncomingQuerySet)
        // check submitted attribute and send response
        this.sendResponseToServer()
    }
    toggleExpansion(){
        this.setState({
            "expanded": ! this.state.expanded ,
            "query_set": this.state.query_set,
            "response_set": this.state.query_set
        })
    }
    handleIncomingQuerySet(message){
        // this method
        // takes an incoming q_set,
        let query_set = []
        // sets state q_set with the attribute "submitted" to false
        for (let i in message.content) {
            let query = message.content[i]
            query.submitted = false
            query_set.push(query)
        }
        this.setState({
            "expanded": this.state.expanded ,
            "query_set": query_set,
            "response_set":null
        })
    }
    handleResponseCallback(query_i, response){
        // this method
        // looks up query with index i
        // validates the response against query.options
        // set state to :
        //  query."submitted" = true
        //  append response to response_set
    }
    sendResponseToServer(){
        // this method
        // sends response_set held in state to server if all query have submitted set to true
        // sets state back to default (empty)
    }
    render(){
        if (this.state.expanded === true) {
            return (
                <div>
                    <ButtonWithAlert
                        className={"utility_button_selected"}
                        alert_active={(this.state.response_set !== null)}/>
                    <div>
                        {this.state.query_set.map((query,i) => (
                            <QueryElement q_type={query.q_type}
                                          key={i}
                                          options={query.options}
                                          submitted={query.submitted}
                                          handleResponseCallback={this.handleResponseCallback}
                            />
                        ))}
                    </div>
                </div>
            )
        } else {
            return(
                <div>
                    <ButtonWithAlert
                        className={"utility_button"}
                        alert_active={(this.state.response_set !== null)}/>
                </div>
            )
        }
    }

}