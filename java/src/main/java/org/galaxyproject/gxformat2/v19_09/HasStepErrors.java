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

import org.galaxyproject.gxformat2.v19_09.utils.Saveable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors</I><br>
 */
public interface HasStepErrors extends Saveable {
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors/errors</I><br>
   *
   * <BLOCKQUOTE>
   *
   * During Galaxy export there may be some problem validating the tool state, tool used, etc.. that
   * will be indicated by this field. The Galaxy user should be warned of these problems before the
   * workflow can be used in Galaxy.
   *
   * <p>This field should not be used in human written Galaxy workflow files.
   *
   * <p>A typical problem is the referenced tool is not installed, this can be fixed by installed
   * the tool and re-saving the workflow and then re-exporting it. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getErrors();
}
