import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const pageVariants = {
  initial: { 
    opacity: 0, 
    y: 20,
    scale: 0.98
  },
  in: { 
    opacity: 1, 
    y: 0,
    scale: 1
  },
  out: { 
    opacity: 0, 
    y: -20,
    scale: 0.98
  }
}

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.4
}

const cardVariants = {
  hidden: { 
    opacity: 0, 
    y: 20,
    scale: 0.95
  },
  visible: { 
    opacity: 1, 
    y: 0,
    scale: 1
  },
  hover: {
    y: -4,
    scale: 1.02,
    transition: {
      duration: 0.2,
      ease: 'easeOut'
    }
  }
}

const modalVariants = {
  hidden: { 
    opacity: 0, 
    scale: 0.8,
    y: 20
  },
  visible: { 
    opacity: 1, 
    scale: 1,
    y: 0
  },
  exit: { 
    opacity: 0, 
    scale: 0.8,
    y: 20
  }
}

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 }
}

// Page transition wrapper
export const PageTransition = ({ children, className = '' }) => (
  <motion.div
    initial="initial"
    animate="in"
    exit="out"
    variants={pageVariants}
    transition={pageTransition}
    className={className}
  >
    {children}
  </motion.div>
)

// Card animation wrapper
export const CardTransition = ({ children, className = '', delay = 0, ...props }) => (
  <motion.div
    initial="hidden"
    animate="visible"
    whileHover="hover"
    variants={cardVariants}
    transition={{
      duration: 0.3,
      delay: delay,
      ease: 'easeOut'
    }}
    className={className}
    {...props}
  >
    {children}
  </motion.div>
)

// Modal transition wrapper
export const ModalTransition = ({ children, isOpen, onClose, className = '' }) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div
        initial="hidden"
        animate="visible"
        exit="exit"
        variants={backdropVariants}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          variants={modalVariants}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className={className}
          onClick={(e) => e.stopPropagation()}
        >
          {children}
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
)

// Stagger animation for lists
export const StaggerContainer = ({ children, className = '' }) => (
  <motion.div
    initial="hidden"
    animate="visible"
    variants={{
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          staggerChildren: 0.1
        }
      }
    }}
    className={className}
  >
    {children}
  </motion.div>
)

// Fade in animation
export const FadeIn = ({ children, delay = 0, duration = 0.5, className = '' }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration, delay }}
    className={className}
  >
    {children}
  </motion.div>
)

// Slide in animation
export const SlideIn = ({ children, direction = 'up', delay = 0, className = '' }) => {
  const directions = {
    up: { y: 20, opacity: 0 },
    down: { y: -20, opacity: 0 },
    left: { x: 20, opacity: 0 },
    right: { x: -20, opacity: 0 }
  }

  return (
    <motion.div
      initial={directions[direction]}
      animate={{ y: 0, x: 0, opacity: 1 }}
      transition={{ duration: 0.4, delay }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Scale animation
export const ScaleIn = ({ children, delay = 0, className = '' }) => (
  <motion.div
    initial={{ scale: 0.8, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    transition={{ duration: 0.3, delay }}
    className={className}
  >
    {children}
  </motion.div>
)

export default {
  PageTransition,
  CardTransition,
  ModalTransition,
  StaggerContainer,
  FadeIn,
  SlideIn,
  ScaleIn
}
