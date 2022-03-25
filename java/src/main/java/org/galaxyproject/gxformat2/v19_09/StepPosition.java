// Copyright Common Workflow Language project contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition</I><br>
 * This interface is implemented by {@link StepPositionImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * This field specifies the location of the step's node when rendered in the workflow editor.
 *
 * </BLOCKQUOTE>
 */
public interface StepPosition extends Savable {
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition/top</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * Relative vertical position of the step's node when rendered in the workflow editor. *
   *
   * </BLOCKQUOTE>
   */
  Object getTop();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition/left</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Relative horizontal position of the step's node when rendered in the workflow editor. *
   *
   * </BLOCKQUOTE>
   */
  Object getLeft();
}
