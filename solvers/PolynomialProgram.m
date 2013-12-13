classdef PolynomialProgram < NonlinearProgram
% Provides a common interface for polynomial optimization.
%  (note: should perhaps be called a SpotPolynomialProgram, to parallel
%  PolynomialSystem/SpotPolynomialSystem)
%  
% Using x to denote the decision variables, attempts to solve the problem
%
%   minimize_x objective(x)
%   subject to 
%         equality_constraints(x) = 0 
%         inequality_constraint(x) >= 0
%
% @option solver can be 'gloptipoly','snopt' (more coming soon)
% @option x0 initial guess

% todo: implement other solution techniques:
%   bertini (via kkt)
%   ... my pcpo idea?  
  
  properties
    decision_variables     % simple msspoly description of x
    objective              % msspoly
    equality_constraints   % msspoly
    inequality_constraints % msspoly
  end

  methods
    function obj = PolynomialProgram(decision_variables,objective,equality_constraints,inequality_constraints)
      typecheck(decision_variables,'msspoly');
      if ~issimple(decision_variables),
        error('decision_variables must be a simple msspoly');
      end
      typecheck(objective,'msspoly');
      if length(objective)~=1
        error('objective must be a scalar msspoly');
      end
      
      if nargin<3, equality_constraints = []; end
      if nargin<4, inequality_constraints = []; end
      if nargin<5, options=struct(); end
      if ~isfield(options,'solver'),
        % todo: check dependencies here and pick my favorite that is also installed
        options.solver = 'snopt';
      end
      
      if ~isfunction(objective,decision_variables)
        error('objective function must only depend on the decision variables');
      end
      if ~isempty(equality_constraints)
        sizecheck(equality_constraints,'colvec');
        if ~isfunction(equality_constraints,decision_variables)
          error('equality constraints must only depend on the decision variables');
        end
      end
      if ~isempty(inequality_constraints)
        sizecheck(inequality_constraints,'colvec');
        if ~isfunction(inequality_constraints,decision_variables)
          error('equality constraints must only depend on the decision variables');
        end
      end

      obj = obj@NonlinearProgram(length(decision_variables),length(equality_constraints),length(inequality_constraints));
      obj.decision_variables = decision_variables;
      obj.objective = objective;
      obj.equality_constraints = equality_constraints;
      obj.inequality_constraints = inequality_constraints;
    end
    
    function [x,objval,exitflag] = solve(obj,x0)
      switch lower(obj.solver)
        otherwise 
          [x,objval,exitflag] = solve@NonlinearProgram(obj,x0);
      end
    end

    function [f,G] = objectiveAndNonlinearConstraints(obj,x)
      poly_f = [obj.objective; obj.equality_constraints; obj.inequality_constraints];
      poly_G = diff(poly_f,obj.decision_variables); % note: i could do this just once
      
      f = double(subs(poly_f,obj.decision_variables,x));
      G = double(subs(poly_G,obj.decision_variables,x));
    end
  end
  
end