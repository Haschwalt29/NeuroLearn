import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .. import db, socketio
from ..models import DebateSession, DebateTurn, DebateScore, User
from ..utils.llm_utils import llm_utils

class DebateService:
    def __init__(self):
        self.llm_utils = llm_utils

    def start_debate(self, user_id: int, topic: str, learner_stance: str, 
                    difficulty: str = "intermediate", settings: Dict = None) -> Dict:
        """Start a new debate session"""
        try:
            # Determine AI stance (opposite of learner stance)
            ai_stance = self._get_opposite_stance(learner_stance)
            
            # Create debate session
            session = DebateSession(
                user_id=user_id,
                topic=topic,
                learner_stance=learner_stance,
                ai_stance=ai_stance,
                difficulty_level=difficulty,
                settings=settings or {},
                llm_model=self.llm_utils.model_name
            )
            
            db.session.add(session)
            db.session.commit()
            
            # Generate initial AI opening statement
            opening_response = self.llm_utils.generate_debate_response(
                topic=topic,
                stance=ai_stance,
                learner_message=f"Let's debate about {topic}. I'm taking the {learner_stance} position.",
                session_context=[]
            )
            
            # Create initial AI turn
            ai_turn = DebateTurn(
                session_id=session.id,
                turn_number=1,
                speaker="ai",
                message=opening_response["message"],
                stance=ai_stance,
                word_count=len(opening_response["message"].split()),
                complexity_score=self._calculate_complexity(opening_response["message"]),
                llm_metadata=opening_response
            )
            
            db.session.add(ai_turn)
            db.session.commit()
            
            # Emit socket event
            socketio.emit('debate_started', {
                'user_id': user_id,
                'session_id': session.id,
                'topic': topic,
                'learner_stance': learner_stance,
                'ai_stance': ai_stance,
                'opening_message': opening_response["message"]
            })
            
            return {
                'session_id': session.id,
                'topic': topic,
                'learner_stance': learner_stance,
                'ai_stance': ai_stance,
                'opening_message': opening_response["message"],
                'difficulty': difficulty
            }
            
        except Exception as e:
            print(f"Error starting debate: {e}")
            db.session.rollback()
            raise e

    def generate_ai_argument(self, session_id: int, learner_message: str) -> Dict:
        """Generate AI response to learner's message"""
        try:
            session = DebateSession.query.get(session_id)
            if not session:
                raise ValueError("Debate session not found")
            
            if session.status != "active":
                raise ValueError("Debate session is not active")
            
            # Validate learner message
            if not learner_message or not learner_message.strip():
                raise ValueError("Learner message cannot be empty")
            
            # Get session context
            context = self._get_session_context(session_id)
            
            # Generate AI response
            start_time = time.time()
            ai_response = self.llm_utils.generate_debate_response(
                topic=session.topic,
                stance=session.ai_stance,
                learner_message=learner_message,
                session_context=context
            )
            response_time = time.time() - start_time
            
            # Create learner turn
            learner_turn = DebateTurn(
                session_id=session_id,
                turn_number=session.total_turns + 1,
                speaker="learner",
                message=learner_message,
                stance=session.learner_stance,
                word_count=len(learner_message.split()),
                response_time=0,  # Learner response time not tracked
                complexity_score=self._calculate_complexity(learner_message)
            )
            db.session.add(learner_turn)
            
            # Create AI turn
            ai_turn = DebateTurn(
                session_id=session_id,
                turn_number=session.total_turns + 2,
                speaker="ai",
                message=ai_response["message"],
                stance=session.ai_stance,
                word_count=len(ai_response["message"].split()),
                response_time=response_time,
                complexity_score=self._calculate_complexity(ai_response["message"]),
                llm_metadata=ai_response
            )
            db.session.add(ai_turn)
            
            # Update session
            session.total_turns += 2
            
            # Score the turns
            learner_scores = self.llm_utils.score_learner_response(
                learner_message, ai_response["message"], session.topic
            )
            
            ai_scores = ai_response.get("scores", {})
            
            # Create score records
            learner_score_record = DebateScore(
                session_id=session_id,
                turn_id=learner_turn.id,
                scorer_type="system",
                logic_score=learner_scores["logic_score"],
                clarity_score=learner_scores["clarity_score"],
                persuasiveness_score=learner_scores["persuasiveness_score"],
                evidence_quality=learner_scores["evidence_quality"],
                critical_thinking=learner_scores["critical_thinking"],
                respectfulness=learner_scores["respectfulness"],
                overall_score=learner_scores["overall_score"],
                improvement_areas=learner_scores["improvement_areas"],
                strengths=learner_scores["strengths"]
            )
            db.session.add(learner_score_record)
            
            ai_score_record = DebateScore(
                session_id=session_id,
                turn_id=ai_turn.id,
                scorer_type="ai",
                logic_score=ai_scores.get("logic_score", 7.0),
                clarity_score=ai_scores.get("clarity_score", 7.0),
                persuasiveness_score=ai_scores.get("persuasiveness_score", 7.0),
                overall_score=sum([
                    ai_scores.get("logic_score", 7.0),
                    ai_scores.get("clarity_score", 7.0),
                    ai_scores.get("persuasiveness_score", 7.0)
                ]) / 3
            )
            db.session.add(ai_score_record)
            
            db.session.commit()
            
            # Emit socket events
            try:
                socketio.emit('debate_turn', {
                    'user_id': session.user_id,
                    'session_id': session_id,
                    'learner_message': learner_message,
                    'ai_message': ai_response["message"],
                    'learner_scores': learner_scores,
                    'turn_number': session.total_turns
                })
            except Exception as socket_error:
                print(f"Socket emit error (non-critical): {socket_error}")
            
            return {
                'ai_message': ai_response["message"],
                'learner_scores': learner_scores,
                'turn_number': session.total_turns,
                'response_time': response_time
            }
            
        except ValueError as e:
            print(f"Validation error in generate_ai_argument: {e}")
            db.session.rollback()
            raise e
        except Exception as e:
            print(f"Error generating AI argument: {e}")
            db.session.rollback()
            raise e

    def switch_stance(self, session_id: int) -> Dict:
        """Switch AI stance mid-debate"""
        try:
            session = DebateSession.query.get(session_id)
            if not session:
                raise ValueError("Debate session not found")
            
            if session.status != "active":
                raise ValueError("Debate session is not active")
            
            # Switch AI stance
            old_stance = session.ai_stance
            session.ai_stance = self._get_opposite_stance(session.ai_stance)
            session.stance_switches += 1
            
            # Generate stance switch message
            switch_message = self.llm_utils.generate_debate_response(
                topic=session.topic,
                stance=session.ai_stance,
                learner_message="[STANCE SWITCH REQUESTED]",
                session_context=self._get_session_context(session_id),
                switch_stance=True
            )
            
            # Create stance switch turn
            switch_turn = DebateTurn(
                session_id=session_id,
                turn_number=session.total_turns + 1,
                speaker="ai",
                message=switch_message["message"],
                stance=session.ai_stance,
                word_count=len(switch_message["message"].split()),
                turn_type="stance_switch",
                llm_metadata=switch_message
            )
            db.session.add(switch_turn)
            
            session.total_turns += 1
            db.session.commit()
            
            # Emit socket event
            socketio.emit('debate_stance_switch', {
                'user_id': session.user_id,
                'session_id': session_id,
                'old_stance': old_stance,
                'new_stance': session.ai_stance,
                'switch_message': switch_message["message"],
                'total_switches': session.stance_switches
            })
            
            return {
                'old_stance': old_stance,
                'new_stance': session.ai_stance,
                'switch_message': switch_message["message"],
                'total_switches': session.stance_switches
            }
            
        except Exception as e:
            print(f"Error switching stance: {e}")
            db.session.rollback()
            raise e

    def end_debate(self, session_id: int) -> Dict:
        """End debate session and calculate final scores"""
        try:
            session = DebateSession.query.get(session_id)
            if not session:
                raise ValueError("Debate session not found")
            
            # Update session status
            session.status = "ended"
            session.ended_at = datetime.utcnow()
            
            # Calculate final scores
            final_scores = self._calculate_final_scores(session_id)
            session.learner_score = final_scores["learner_score"]
            session.ai_score = final_scores["ai_score"]
            session.debate_quality = final_scores["debate_quality"]
            
            db.session.commit()
            
            # Emit socket event
            socketio.emit('debate_ended', {
                'user_id': session.user_id,
                'session_id': session_id,
                'final_scores': final_scores,
                'total_turns': session.total_turns,
                'stance_switches': session.stance_switches
            })
            
            return {
                'session_id': session_id,
                'final_scores': final_scores,
                'total_turns': session.total_turns,
                'stance_switches': session.stance_switches,
                'debate_duration': (session.ended_at - session.created_at).total_seconds()
            }
            
        except Exception as e:
            print(f"Error ending debate: {e}")
            db.session.rollback()
            raise e

    def get_debate_session(self, session_id: int) -> Dict:
        """Get debate session details"""
        try:
            print(f"🔍 Getting debate session {session_id}")
            session = DebateSession.query.get(session_id)
            if not session:
                print(f"❌ Session {session_id} not found")
                raise ValueError("Debate session not found")
            
            print(f"✅ Found session: {session.topic}, status: {session.status}")
            
            # Get all turns
            turns = DebateTurn.query.filter_by(session_id=session_id).order_by(DebateTurn.turn_number).all()
            print(f"📝 Found {len(turns)} turns")
            
            # Get scores
            scores = DebateScore.query.filter_by(session_id=session_id).all()
            print(f"📊 Found {len(scores)} scores")
            
            return {
                'session': {
                    'id': session.id,
                    'topic': session.topic,
                    'learner_stance': session.learner_stance,
                    'ai_stance': session.ai_stance,
                    'status': session.status,
                    'total_turns': session.total_turns,
                    'stance_switches': session.stance_switches,
                    'learner_score': session.learner_score,
                    'ai_score': session.ai_score,
                    'debate_quality': session.debate_quality,
                    'created_at': session.created_at.isoformat(),
                    'ended_at': session.ended_at.isoformat() if session.ended_at else None
                },
                'turns': [
                    {
                        'id': turn.id,
                        'turn_number': turn.turn_number,
                        'speaker': turn.speaker,
                        'message': turn.message,
                        'stance': turn.stance,
                        'word_count': turn.word_count,
                        'created_at': turn.created_at.isoformat(),
                        'turn_type': turn.turn_type
                    }
                    for turn in turns
                ],
                'scores': [
                    {
                        'id': score.id,
                        'turn_id': score.turn_id,
                        'scorer_type': score.scorer_type,
                        'logic_score': score.logic_score,
                        'clarity_score': score.clarity_score,
                        'persuasiveness_score': score.persuasiveness_score,
                        'evidence_quality': score.evidence_quality,
                        'critical_thinking': score.critical_thinking,
                        'respectfulness': score.respectfulness,
                        'overall_score': score.overall_score,
                        'improvement_areas': score.improvement_areas,
                        'strengths': score.strengths
                    }
                    for score in scores
                ]
            }
            
        except Exception as e:
            print(f"❌ Error getting debate session {session_id}: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise e

    def get_user_debate_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's debate history"""
        try:
            sessions = DebateSession.query.filter_by(user_id=user_id).order_by(
                DebateSession.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': session.id,
                    'topic': session.topic,
                    'learner_stance': session.learner_stance,
                    'ai_stance': session.ai_stance,
                    'status': session.status,
                    'total_turns': session.total_turns,
                    'stance_switches': session.stance_switches,
                    'learner_score': session.learner_score,
                    'debate_quality': session.debate_quality,
                    'created_at': session.created_at.isoformat(),
                    'ended_at': session.ended_at.isoformat() if session.ended_at else None
                }
                for session in sessions
            ]
            
        except Exception as e:
            print(f"Error getting debate history: {e}")
            return []

    def _get_opposite_stance(self, stance: str) -> str:
        """Get opposite stance"""
        stance_mapping = {
            "pro": "con",
            "con": "pro", 
            "neutral": "pro",  # Changed from "con" to "pro" for better debates
            "for": "against",
            "against": "for"
        }
        return stance_mapping.get(stance.lower(), "pro")  # Default to "pro" instead of "con"

    def _get_session_context(self, session_id: int, limit: int = 10) -> List[Dict]:
        """Get recent session context"""
        turns = DebateTurn.query.filter_by(session_id=session_id).order_by(
            DebateTurn.turn_number.desc()
        ).limit(limit).all()
        
        return [
            {
                "speaker": turn.speaker,
                "message": turn.message,
                "stance": turn.stance,
                "turn_number": turn.turn_number
            }
            for turn in reversed(turns)
        ]

    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-1)"""
        words = text.split()
        if not words:
            return 0.0
        
        # Simple complexity metrics
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        avg_sentence_length = len(words) / max(sentence_count, 1)
        
        # Complex words (more than 6 characters)
        complex_words = len([w for w in words if len(w) > 6])
        complex_word_ratio = complex_words / len(words)
        
        # Calculate complexity score
        complexity = (
            min(avg_word_length / 10, 1.0) * 0.3 +
            min(avg_sentence_length / 20, 1.0) * 0.4 +
            min(complex_word_ratio * 2, 1.0) * 0.3
        )
        
        return min(1.0, complexity)

    def _calculate_final_scores(self, session_id: int) -> Dict:
        """Calculate final debate scores"""
        # Get all learner scores
        learner_scores = DebateScore.query.filter_by(
            session_id=session_id,
            scorer_type="system"
        ).all()
        
        if not learner_scores:
            return {
                "learner_score": 0.0,
                "ai_score": 0.0,
                "debate_quality": 0.0
            }
        
        # Calculate averages
        learner_score = sum(score.overall_score for score in learner_scores) / len(learner_scores)
        
        # Get AI scores
        ai_scores = DebateScore.query.filter_by(
            session_id=session_id,
            scorer_type="ai"
        ).all()
        
        ai_score = 0.0
        if ai_scores:
            ai_score = sum(score.overall_score for score in ai_scores) / len(ai_scores)
        
        # Calculate debate quality (combination of both scores and engagement)
        session = DebateSession.query.get(session_id)
        engagement_factor = min(1.0, session.total_turns / 20)  # More turns = better engagement
        quality_factor = (learner_score + ai_score) / 2
        
        debate_quality = (quality_factor * 0.7 + engagement_factor * 0.3) * 10
        
        return {
            "learner_score": round(learner_score, 2),
            "ai_score": round(ai_score, 2),
            "debate_quality": round(debate_quality, 2)
        }

# Global service instance
debate_service = DebateService()
