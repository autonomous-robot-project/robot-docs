# **Excerto de *Artificial Intelligence and Mobile Robots (Gat 1998\)***

## **The Anatomy of the Three-layer Architecture**

The three-layer architecture consists of three components: a reactive feedback control mechanism, a reactive plan-execution mechanism, and a mechanism for performing time-consuming deliberative computations. These components run as separate computational processes. This is most easily accomplished by using a multitasking or multithreaded operating system, but it can also be done by carefully coding the algorithms so they can be manually interleaved within a single computational process.  
In 3T the components are called the skill layer, the sequencing layer, and the planning layer, respectively. In **ATLANTIS** these layers are called the controller, the sequencer, and the deliberator. The following discussion uses the **ATLANTIS** terminology, but as much as possible the description is generic to all incarnations of the three-layer architecture.

### **The Controller**

The controller consists of one or more threads of computation that implement one or more feedback control loops, tightly coupling sensors to actuators. The transfer function(s) computed by the controller can be changed at run time. Usually the controller contains a library of hand-crafted transfer functions (called primitive behaviors or skills). Which ones are active at any given time is determined by an external input to the controller.  
To distinguish between the code that implements a transfer function and the physical behavior produced by that transfer function when running on a robot in an environment, we shall capitalize the latter. Thus, a Behavior is a piece of code that produces a behavior when it is running. Primitive Behaviors are designed to produce simple primitive behaviors that can be composed to produce more complex task-achieving behavior (a job done, naturally, by the sequencer). Classic examples of primitive behaviors are.wall-following, moving to a destination while avoiding collisions, and moving through doorways.  
There are several important architectural constraints on the algorithms that go into the controller. First, computing one iteration of the transfer function should be of constant-bounded time and space complexity, and this constant should be small enough to provide enough bandwidth to afford stable closed-loop control for the desired behavior.  
Second, the algorithms in the controller should fail cognizantly; that is, they should be designed to detect (as opposed to avoid) any failure to perform the function for which they were designed (cf. Noreils 1990). Rather than attempt to design algorithms that never fail (which is impossible on real robots), one can instead design algorithms that never fail to detect a failure. This allows other components of the system (the sequencer and deliberator) to take corrective action to recover from the failure.  
Third, the use of internal state should be avoided whenever possible. An important exception to this rule is filtering algorithms, which rely on internal state, but can nevertheless be used in the controller. If internal state is used for other purposes, it should be ephemeral; that is, it should expire after some constant-bounded time. This way, if the semantics of the internal state do not reflect the true state of affairs in the environment, at least the time during which this error will manifest itself will be bounded.  
	Finally, internal state in the controller should not introduce discontinuities (in the mathematical sense) in a Behavior. In other words, a Behavior (which is a transfer function) should be a continuous function with respect to its internal state. It is the responsibility of the sequencer to manage transitions between regimes of continuous operation.  
A number of special-purpose languages have been developed for programming the controller (e.g., Gat 1991a; Brooks 1989), but any language can be used as long as the architectural constraints are observed. Most of the special-purpose languages for programming the controller were developed at a time when robots could support only very small processors for which no other development tools were available. The current trend is to simply program the controller in C.

### **The Sequencer**

The sequencer’s job is to select which primitive Behavior (i.e., which transfer function) the controller should use at a given time, and to supply parameters for the Behavior. By changing primitive Behaviors at strategic moments, the robot can be coaxed into performing useful tasks. The problem, of course, is that the outcome of selecting a particular primitive in a particular situation might not be the intended one, and so a simple linear sequence of primitives is unreliable.  
The sequencer must be able to respond conditionally to the current situation, whatever it might be.  
One approach to the problem is to enumerate all the possible states the robot can be in and precompute the correct primitive to use in each state for a particular task. Clever encoding can actually make this daunting task tractable for certain constrained domains (Schoppers 1987). However, this universal plan approach has two serious drawbacks.  
First, it is often not possible for a robot to know its current state, especially when unexpected contingencies arise. Second, this approach disregards the robot's execution history, which often contains useful information.  
An alternative is to use an approach called conditional sequencing, which is a more complex model of plan execution motivated by human instruction following. Humans can achieve tasks based on very concise instructions in the face of a wide variety of contingencies (e.g., Agre 1990; Suchman 1987).  
Conditional sequencing provides a computational framework for encoding the sort of procedural knowledge contained in instructions. It differs from traditional plan execution in that the control constructs for composing primitives are not limited to the partial ordering, conditionals, and loops used to build SPA plans. Conditional sequencing systems include constructs for responding to contingencies, and managing multiple parallel interacting tasks.  
It is possible to construct a conditional sequencing system in a traditional programming language like C, but because the control constructs are so much more complex than those provided by such languages, conditional sequencing is much more effectively done with a special-purpose language like RAPs (Firby 1989), PRS (Georgeff 1987), the Behavior Language (Brooks 1989), REX/GAPPS (Kaelbling 1987, Kaelbling 1989, Bonasso 1992), or ESL (Gavi997): There are two major approaches to the design of conditional sequencing languages. They can be complete languages in their own right with their own specialized execution semantics. RAPs and PRS take this approach. Or they can be layered on top of a syntactically extensible programming language like Lisp.  
This is the approach taken by the Behavior Language and ESL. Furthermore, the structure of the language can treat all possible outcomes of an action in a homogeneous fashion, or the language can be structured to recognize a privileged “nominal” result of an action and treat all other outcomes as “failures.”  
Again, RAPs and PRS take the first approach; ESL takes the second. Which approach one chooses depends on what one is trying to do. The RAPs/PRS approach results in a more circumscribed language that is suitable for use as a representation for an automated planner. The ESL approach, because it subsumes a traditional programming language, is more convenient to use and easier to extend, but more difficult to analyze.  
The sequencer should not perform computations that take a long time relative to the rate of environmental change at the level of abstraction presented by the controller. Exactly how long a “long time” is depends on both the environment and the repertoire of Behaviors. Usually this constraint implies that the sequencer should not perform any search or temporal projection, but it might also constrain, for example, certain vision-processing algorithms from appearing in the sequencer, especially if computational resources are limited.

### **The Deliberator**

The deliberator is the locus of time-consuming computations. Usually this means such things as planning and other exponential search-based algorithms, but as noted before, it could also include polynomial-time algorithms with large constants such as certain vision processing algorithms in the face of limited computational resources. The key architectural feature of the deliberator is that several Behavior transitions can occur between the time a deliberative algorithm is invoked and the time it produces a result. The deliberator runs as one or more separate threads of control. There are no architectural constraints on algorithms in the deliberator, which are invariably written using standard programming languages.  
The deliberator can interface to the rest of the system in two different ways. It can produce plans for the sequencer to execute, or it can respond to specific queries from the sequencer. The RAPs-based 3T architecture takes the first approach (Bonasso et al. 1997). The ESL-based ATLANTIS architecture takes the second approach. This is a natural result of the fact that RAPs was designed specifically to serve as a plan representation for an automated planning system, and ESL was not. These two approaches are not mutually exclusive. RAPs does permit deliberative algorithms (called RAP-experts) to be invoked at run-time to answer specific queries, and the ATLANTIS sequencer can ask the deliberator to give it a complete plan, which it then executes. (This is being done in an application of ESL to autonomous spacecraft (Pell et al. 1996).)

## **Case Study**

To date at least half a dozen different robots have been programmed using some variation of the three-layer architecture (Gat 1992; Gat and Dorais 1994; Nourbakhsh et al.; Elsaessar and Slack 1994; Connell 1991; Firby 1996; Bonasso et al. 1997; Firby and Slack 1995). I will describe one of these here in some detail.

Alfred is a B12 robot built by Real World Interface (RWI). The B12 is a cylindrical robot, twelve inches in diameter, with a synchrodrive mobility mechanism. Encoders on the drive and steering motors provide fairly reliable odometry and dead reckoning, although the robot's heading tends to precess because of slight misalignments of its wheels. A development enclosure houses a Gespak 68000 computer and a radially symmetric ring of twelve Polaroid sonars (Biber 1980). The sonars are mounted on panels that are easily reconfigured. The sonar configuration was rotated fifteen degrees from the default factory configuration, resulting in one sonar pointing straight forward in the direction of motion and one sonar pointing directly to either side (see figure 2). This turned out empirically to make wall-following more reliable.

*Figure 2\. Schematic top-view of Alfred showing sonar directions (radial arrows) relative to the direction of motion (dark central arrow) and obstacle-detection regions.*

Alfred also used a Macintosh Powerbook Duo230 running Macintosh Common Lisp (MCL) mounted on top of the robot. The Duo was connected to the Gespak board through an RS-232 serial port running at 9600 baud. Alfred's controller ran on the Gespak board. The sequencer and deliberator were programmed in Lisp and ran on the Powerbook.

Alfred was programmed to compete in two events at the 1993 AAAI mobile robot contest (Nourbakhsh et al. 1993). The first event was called "escape from the office" and involved finding a route out of a room filled with furniture, and traversing across a large open area filled with cardboard boxes. The second event was called "deliver the coffee" and involved self-localization and path-planning in a maze.

Alfred placed second in the first event, and was the only robot to complete the second event. All the contest-specific code for the robot was written in three days by one person.

The following sections describe the control, sequencing, and deliberative layers on Alfred. These descriptions are faithful to the actual implementation used in the contest, and could no doubt be improved.

### **Control Layer**

Alfred's control layer was implemented in a language for action (ALFA) (Gat 1991a), a programming language designed to enforce the control layer's architectural constraints. ALFA is a dataflow language with no looping constructs. It does, however, have state variables, making it Turing-complete. It is therefore possible to implement arbitrary algorithms in ALFA, and so ALFA's constraint enforcement is far from perfect. The language does not make it impossible to violate the rules, just more difficult. Unfortunately, it turns out that ALFA's design also makes it more difficult to do things that should be allowed in the control layer. I no longer advocate the use of ALFA, preferring instead to use C or Lisp and a little self-discipline to enforce the architectural constraints.

Alfred's control layer had five interesting behaviors: obstacle avoidance, wall finding, wall alignment, wall following, and wandering. (It also had a number of uninteresting but nonetheless useful behaviors like turning in place.)

Obstacle avoidance was done as follows. First, the sonar data was preprocessed to indicate the presence or absence of an obstacle in each of five regions around the front of the robot. (The five rear-facing sonars were not used.) There was a near-field "hard obstacle" region close to the front of the robot (figure 2, dark shading), and three "soft obstacle" regions farther away. The hard obstacle region was divided into left and right regions that overlapped at the front sonar. The robot was able to detect collisions by monitoring its motor current. The obstacle regions were egg-shaped, extending farther from the robot toward the front than at the sides.

At the core of the controller code was the following safety algorithm that was always running:

IF there is a collision while moving forward  
    BACK UP slowly for a few seconds  
ELSE IF there is a collision while moving backwards  
    STOP for a few seconds  
ELSE IF there is an obstacle in one of the hard obstacle regions  
    STOP  
ELSE IF there is an obstacle in one of the soft obstacle regions  
    set the current speed to SLOW  
ELSE (there are no obstacles)  
    gradually increase forward speed up to a maximum value.

This code had the effect of slowing the robot down in the presence of obstacles and stopping the robot when it was in imminent danger of collision. By allowing any detected obstacle to immediately slow the robot down, but only a succession of clear readings to speed it back up again, the robot reliably slowed down in cluttered areas even if there was a lot of specular reflection.

The code uses internal state to remember collisions for a few seconds after they happen and to keep track of the current maximum speed. This use of internal state obeys the controller's architectural constraints in the first case because it is ephemeral, and in the second case because it is part of a filtering algorithm. The filtering algorithm might appear to violate the prohibition on state-dependent discontinuities, but this is not the case. The output of the controller is a continuous function of the state; it is the value of the state that changes discontinuously over time.

Ideally, the collision response routine would have been put in the sequencer, but because the robot detected collisions by monitoring motor current, by the time a collision was detected there was already quite a bit of mechanical stress built up in the robot's drive mechanism. Simply stopping the robot would have caused the robot's motor servo controller to attempt to maintain the motor's velocity at zero, which would have maintained this mechanical stress. Relieving the stress required backing up, and to accomplish this as quickly as possible, the response was implemented in the controller. This is a good example of how the lines between the components of the three-layer architecture can be blurred to accommodate reality.

Obstacle avoidance was done with the following algorithm:

IF there is an obstacle in the soft-left obstacle region and not in the soft-right region  
    turn slowly to the right  
ELSE IF there is an obstacle in the soft-right obstacle region but not in the soft-left obstacle region  
    turn slowly to the left  
ELSE  
    go straight, or turn toward a commanded heading.

This algorithm avoids obstacles only when the choice of turning direction is clearly dictated by the situation. When an obstacle is directly in front, the robot does not turn. This is because the control layer has no information on which to base the choice of a turning direction, and so this choice is deferred to the sequencer.

Wall finding was done by turning toward the sonar with the shortest range reading until the shortest reading was given by the forward sonar, and simultaneously moving forward until forced to stop by an obstacle in a hard obstacle region. This would reliably leave the robot facing the nearest object. When initiated near a wall, the robot would turn toward the wall.

Wall alignment was done by slowly turning the robot until a discontinuity caused by the onset of specular reflection was seen in the range reading returned by the forward sonar. When this procedure was begun while facing a smooth wall, the angle at which the discontinuity occurred was reproducible to better than one degree.

Wall following was done by servoing the robot's heading to the reading on a side-facing sonar while moving forward. Although conceptually simple, the actual implementation is complicated by a number of factors.

The primary problem is that a straightforward negative-feedback servo loop off a side-facing sonar is unstable if the robot ever turns far enough toward the wall to cause a specular reflection on the side sonar. When this happens, it appears to the robot that the wall is suddenly very far away, and it will continue to turn toward the wall and eventually collide unless the safety module stops it. A similar effect happens when the robot passes an open door or an intersecting corridor.

There are two possible solutions to this problem. The first is to servo to the shortest reading on the side-facing sonar and its two adjacent sonars. The second is to use a model-based estimation algorithm such as a Kalman filter to compute the distance to the wall. The solution used on Alfred was a model-based estimator (though not a Kalman filter) that simply rejected any sonar reading that was much greater than the last known distance to the wall. The estimator also kept track of the robot's heading and odometer reading (i.e., the drive motor encoder reading) every time a valid sonar reading was taken. When an invalid sonar reading occurred, the robot turned toward the heading it was on during the last valid reading. If the robot traveled more than two meters without a valid reading, the robot stopped.

All of these primitive behaviors were implemented in less than 200 lines of ALFA code.

### **Sequencing Layer**

Alfred's sequencing code was written in Macintosh Common Lisp version 2.0 (with one exception; see below), using a set of macros that later evolved into ESL (Gat 1997). MCL 2.0 is a single-threaded Lisp, which made it impossible to implement multithreaded task management directly. MCL version 3 is multithreaded, and all of the code and infrastructure described in this section have been much improved since Alfred's code was written.

The first contest event required the robot to search an office-like environment for a door, then traverse an obstacle-strewn area to a finish line. The door was opened between one and three minutes after the start of the event, and it could be in one of three different locations. The robot was told its initial orientation and the size of the room, but not its initial position nor the locations of obstacles.

Alfred determined its location by wandering randomly for one minute and keeping track of its maximum and minimum positions along the x and y axes. Wandering was done by augmenting the obstacle-avoidance code with an algorithm for choosing a turn direction when the choice was not clear from the current situation. This must be done with some care, or the robot can get stuck in an infinite loop. Alfred used the following algorithm: when an ambiguous obstacle avoidance situation was encountered, the robot would do an angular scan, turning first one way, then the other. The angle of the turn was gradually increased until the robot was able to move forward some threshold distance without triggering the scan. The scan angle was then reset to its initial value. Alfred's wander behavior was actually written in ALFA, although its use of stored internal state to produce discontinuous behavior indicates that it should be considered part of the sequencing layer.

Alfred then attempted to escape from the office by trying each of the three door locations in turn. It would move to the center of the office, point itself towards one of the doors, and turn on the follow-current-heading-with-obstacle-avoidance primitive. It would then wait until either it escaped the office (as indicated by its dead-reckoning position), in which case it headed toward the finish line, or a time limit was reached, in which case it tried the next door. This task required no planning.

The second contest was much more interesting and challenging. The robot was put in a maze for which it had been given a complete and accurate map. However, the robot was given no information about its initial position or orientation. The robot's task was to search for a coffeepot hidden in the maze and deliver it to a given destination. The robot was given partial information about the location of the coffeepot. Of course, Alfred had no sensors capable of detecting a coffeepot, so it had to be told when the coffeepot was nearby, but otherwise Alfred completed the task with no cheating.

The key to Alfred's success was a combination of behaviors that allowed for reliable navigation of environments that were rich in walls, like mazes, and some creative representations. In addition to representing the a priori map of the maze in terms of open space, the robot was also given a description of the maze in terms of the wall assemblies it comprised. (With a little more time the robot could have been programmed to convert from one representation to the other automatically.)

The robot self-localized by first locating a wall. It did this by invoking the wall-finding primitive and then verifying that it had indeed found a wall rather than an obstacle by attempting to follow it for some distance (two meters). It then began to follow the wall, turning whenever the wall turned, and keeping track of the sequence of turns. Whenever it made a turn, it checked to see if the sequence of turns it had made created an unambiguous match with its a priori knowledge of the shapes of the wall assemblies in the maze. (This was done by the deliberator.) As soon as it had a match, the robot knew where it was. It then began a systematic search of the possible locations of the coffeepot, followed by a traversal to the delivery location.

Note that the algorithms in the sequencer make extensive use of internal state (keeping track of which door location is being tried, maintaining records of the robot's position, etc.) but no search or temporal projection.

### **Deliberative Layer**

The deliberative layer did the matching of Alfred's self-localization sequence to the a priori map and also planned paths for traveling between locations. Both algorithms were simple exhaustive searches made tractable by the fact that the search space was bounded by the size of the maze.

By the standards of AI, the deliberative layer was trivial and uninteresting, which is precisely what makes the three-layer architecture nontrivial and very interesting. The use of a sequencing layer makes it possible (in fact, easy) to use trivial and uninteresting algorithms to control real robots performing complex tasks.

## **Discussion**

The architectural guidelines that govern the design of the three-layer architecture are not derived from fundamental theoretical considerations. Instead, they are derived from empirical observations of the properties of environments in which robots are expected to perform, and of the algorithms that have proven useful in controlling them. Robot algorithms tend to fall into three major equivalence classes: fast, mostly stateless reactive algorithms with hard real-time bounds on execution time, slow deliberative algorithms like planning, and intermediate algorithms which are fairly fast, but cannot provide hard real-time guarantees.  
“Fast” and “slow” are measured with respect to the rate of change of the environment. In principle, if the rate of change of the environment is sufficiently slow (or, equivalently, if a planner were available that was sufficiently fast) the controller could contain a planner. (Note that this situation is essentially equivalent to the SPA architecture.) It is usually not possible to build planners that are fast enough to operate in this manner in realistic environments

## **Conclusions**

The three-layer architecture arises from the empirical observation that effective algorithms for controlling mobile robots tend to fall into three distinct categories:  
(1) reactive control algorithms which map sensors directly onto actuators with little or no internal state;  
(2) algorithms for governing routine sequences of activity which rely extensively on internal state but perform no search; and  
(3) time-consuming (relative to the rate of change of the environment) search-based algorithms such as planners. The three-layer architecture is based on the premise that algorithms of the first (second) type can provide effective computational abstractions for constructing interfaces to algorithms of the second (third) type.  
This conclusion has apparently been reached independently by at least three different groups of researchers. Algorithms of the first and third type can be programmed in conventional programming languages. Algorithms of the second type appear to benefit significantly from specialized languages with sophisticated control constructs. Attempts to construct languages to enforce the constraints imposed on algorithms of the first type have been largely unsuccessful. In retrospect, in the story of the three-layer architecture there may be more to be learned about research methodology than about robot control architectures.  
For many years, the field was bogged down in the assumption that planning was sufficient for generating intelligent behavior in situated agents. That it is not sufficient clearly does not justify the conclusion that planning is therefore unnecessary. A lot of effort has been spent defending both of these extreme positions. Some of this passion may be the result of a hidden conviction on the part  
of AI researchers that at the root of intelligence lies a single, simple, elegant mechanism. But if, as seems likely, there is no One True Architecture, and intelligence relies on a hodgepodge of techniques, then the three-layer architecture  
offers itself as a way to help organize the mess.  
The three-layer architecture is by no means the last word in either architectures or organizational tools. It largely ignores, for example, issues like sensor processing, learning, and world modeling. Such algorithms may turn out to fit nicely within the existing structure, or it may prove necessary to extend the architecture to incorporate them. This promises to be fertile ground for future research.